from django import forms

class SymbolLookup(forms.Form):
    symbol_lookup = forms.CharField(label='Symbol Lookup', max_length=100)
