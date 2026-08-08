from django import forms

from order.models import City, Province


class ProvinceForm(forms.ModelForm):
    class Meta:
        model = Province
        fields = ["name", "is_active", "sort_order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        self.fields["sort_order"].widget.attrs["class"] = "form-control"


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ["province", "name", "is_active", "sort_order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].queryset = Province.objects.all().order_by(
            "sort_order", "name"
        )
        self.fields["province"].widget.attrs["class"] = "form-select"
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        self.fields["sort_order"].widget.attrs["class"] = "form-control"
