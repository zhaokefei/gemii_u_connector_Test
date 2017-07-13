# /usr/bin/env python
# -*- coding:utf-8 -*-

from django import forms

class KickingForm(forms.Form):
    ayd_task = forms.ChoiceField(label='爱婴岛踢人开关', choices=(('open', '开'), ('close', '关')))
    msj_task = forms.ChoiceField(label='美素佳儿踢人开关', choices=(('open', '开'), ('close', '关')))
    wyeth_task = forms.ChoiceField(label='惠氏踢人开关', choices=(('open', '开'), ('close', '关')))