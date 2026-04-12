import warnings
import math
from typing import Optional, Tuple, Union

import torch
import torch.nn as nn
from transformers import Wav2Vec2PreTrainedModel, Wav2Vec2Model
from transformers.modeling_outputs import CausalLMOutput

_HIDDEN_STATES_START_POSITION = 2


def _no_grad_trunc_normal_(tensor, mean, std, a, b):
    def norm_cdf(x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    with torch.no_grad():
        l = norm_cdf((a - mean) / std)
        u = norm_cdf((b - mean) / std)
        tensor.uniform_(2 * l - 1, 2 * u - 1)
        tensor.erfinv_()
        tensor.mul_(std * math.sqrt(2.0))
        tensor.add_(mean)
        tensor.clamp_(min=a, max=b)
        return tensor


def trunc_normal_(tensor, mean=0.0, std=1.0, a=-2.0, b=2.0):
    return _no_grad_trunc_normal_(tensor, mean, std, a, b)


class Wav2Vec2ForWav2Vec2ForCTCAndUttranceRegression(Wav2Vec2PreTrainedModel):
    def __init__(self, config, target_lang: Optional[str] = None):
        super().__init__(config)
        self.wav2vec2 = Wav2Vec2Model(config)
        self.dropout = nn.Dropout(config.final_dropout)

        self.target_lang = target_lang
        if config.vocab_size is None:
            raise ValueError(
                "You are trying to instantiate {self.__class__} with a configuration that "
                "does not define the vocabulary size of the language model head. Please "
                "instantiate the model as follows: `Wav2Vec2ForCTC.from_pretrained(..., vocab_size=vocab_size)`. "
                "or define `vocab_size` of your model's configuration."
            )

        output_hidden_size = (
            config.output_hidden_size if hasattr(config, "add_adapter") and config.add_adapter else config.hidden_size
        )
        self.lm_head = nn.Linear(output_hidden_size, config.vocab_size)

        self.cls_token1 = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.mlp_head_utt1 = nn.Sequential(nn.LayerNorm(config.hidden_size), nn.Linear(config.hidden_size, 1))

        self.cls_token2 = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.mlp_head_utt2 = nn.Sequential(nn.LayerNorm(config.hidden_size), nn.Linear(config.hidden_size, 1))

        self.cls_token3 = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.mlp_head_utt3 = nn.Sequential(nn.LayerNorm(config.hidden_size), nn.Linear(config.hidden_size, 1))

        self.cls_token4 = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.mlp_head_utt4 = nn.Sequential(nn.LayerNorm(config.hidden_size), nn.Linear(config.hidden_size, 1))

        self.post_init()
        trunc_normal_(self.cls_token1, std=0.092)
        trunc_normal_(self.cls_token2, std=0.01)
        trunc_normal_(self.cls_token3, std=0.052)
        trunc_normal_(self.cls_token4, std=0.02)

    def tie_weights(self):
        if self.target_lang is not None and getattr(self.config, "adapter_attn_dim", None) is None:
            raise ValueError(f"Cannot pass `target_lang`: {self.target_lang} if `config.adapter_attn_dim` is not defined.")
        elif self.target_lang is None and getattr(self.config, "adapter_attn_dim", None) is not None:
            print("By default `target_lang` is set to 'eng'.")
        elif self.target_lang is not None:
            self.load_adapter(self.target_lang, force_load=True)

    def freeze_feature_extractor(self):
        warnings.warn(
            "The method `freeze_feature_extractor` is deprecated and will be removed in Transformers v5. "
            "Please use the equivalent `freeze_feature_encoder` method instead.",
            FutureWarning,
        )
        self.freeze_feature_encoder()

    def freeze_feature_encoder(self):
        self.wav2vec2.feature_extractor._freeze_parameters()

    def freeze_base_model(self):
        for param in self.wav2vec2.parameters():
            param.requires_grad = False

    def forward(
        self,
        input_values: torch.Tensor,
        attention_mask: Optional[torch.LongTensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        labels = None,
    ) -> Union[Tuple, CausalLMOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        B, T = input_values.size()

        extract_features = self.wav2vec2.feature_extractor(input_values)
        extract_features = extract_features.transpose(1, 2)

        if attention_mask is not None:
            attention_mask = self.wav2vec2._get_feature_vector_attention_mask(
                extract_features.shape[1], attention_mask, add_adapter=False
            )

        hidden_states, extract_features = self.wav2vec2.feature_projection(extract_features)
        hidden_states = self.wav2vec2._mask_hidden_states(
            hidden_states, mask_time_indices=None, attention_mask=attention_mask
        )

        cls_token1 = self.cls_token1.expand(B, -1, -1)
        cls_token2 = self.cls_token2.expand(B, -1, -1)
        cls_token3 = self.cls_token3.expand(B, -1, -1)
        cls_token4 = self.cls_token4.expand(B, -1, -1)
        hidden_states = torch.cat((cls_token1, cls_token2, cls_token3, cls_token4, hidden_states), dim=1)
        outputs = self.wav2vec2.encoder(
            hidden_states,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        hidden_states = outputs[0]
        hidden_states = self.dropout(hidden_states)

        u1 = self.mlp_head_utt1(hidden_states[:, 0])
        u2 = self.mlp_head_utt2(hidden_states[:, 1])
        u3 = self.mlp_head_utt3(hidden_states[:, 2])
        u4 = self.mlp_head_utt4(hidden_states[:, 3])

        logits = self.lm_head(hidden_states[:, 4:])
        loss = None

        if labels is not None:
            labels, utt_label = labels['labels'], labels['utt_label'][:, :4]
            if labels.max() >= self.config.vocab_size:
                raise ValueError(f"Label values must be <= vocab_size: {self.config.vocab_size}")

            attention_mask = (
                attention_mask if attention_mask is not None else torch.ones_like(input_values, dtype=torch.long)
            )
            input_lengths = self._get_feat_extract_output_lengths(attention_mask.sum(-1)).to(torch.long)

            labels_mask = labels >= 0
            target_lengths = labels_mask.sum(-1)
            flattened_targets = labels.masked_select(labels_mask)

            log_probs = nn.functional.log_softmax(logits, dim=-1, dtype=torch.float32).transpose(0, 1)

            with torch.backends.cudnn.flags(enabled=False):
                utt_preds = torch.cat((u1, u2, u3, u4), dim=1)
                loss_utt = nn.functional.mse_loss(utt_preds, utt_label)
                loss_ph = nn.functional.ctc_loss(
                    log_probs,
                    flattened_targets,
                    input_lengths,
                    target_lengths,
                    blank=self.config.pad_token_id,
                    reduction=self.config.ctc_loss_reduction,
                    zero_infinity=self.config.ctc_zero_infinity,
                )
                loss = loss_utt + loss_ph

        if not return_dict:
            output = (logits,) + outputs[_HIDDEN_STATES_START_POSITION:]
            return ((loss,) + output) if loss is not None else output

        return CausalLMOutput(
            loss=loss,
            logits={
                'logits': logits,
                'accuracy': u2,
                'fluency': u1,
                'total score': u3,
                'content': u4,
            },
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
