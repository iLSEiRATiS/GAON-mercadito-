# users/forms.py
from django import forms
from .models import CustomUser

def resolve_user_email(user):
    # 1) Si ya lo tiene el usuario
    if user and getattr(user, "email", ""):
        return user.email

    # 2) Buscar en EmailAddress (allauth)
    try:
        from allauth.account.models import EmailAddress
        e = (EmailAddress.objects
             .filter(user=user)
             .order_by("-verified", "-primary")
             .first())
        if e:
            return e.email
    except Exception:
        pass

    # 3) Buscar en SocialAccount.extra_data
    try:
        from allauth.socialaccount.models import SocialAccount
        sa = SocialAccount.objects.filter(user=user).first()
        if sa and sa.extra_data:
            data = sa.extra_data or {}
            # Google: 'email' ; GitHub puede venir en la lista de emails de la API
            if "email" in data:
                return data.get("email") or ""
            # fallback por si algún proveedor usa otra key
            return data.get("emailAddress", "") or data.get("mail", "")
    except Exception:
        pass

    return ""

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "telefono"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Usuario"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Apellido"}),
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),  # se bloquea edición
            "telefono": forms.TextInput(attrs={"placeholder": "Teléfono"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Nunca editable, pero queremos mostrarlo
        self.fields["email"].disabled = True
        self.fields["email"].required = True

        # Resolver email real (DB o social)
        resolved = resolve_user_email(self.instance)
        # Mostrarlo como valor (para que se vea siempre)
        if resolved:
            self.initial["email"] = resolved
            # Y además como placeholder (por si el navegador limpia value)
            self.fields["email"].widget.attrs["placeholder"] = resolved
        else:
            # fallback neutro
            self.fields["email"].widget.attrs["placeholder"] = "tu@email.com"

    def clean_email(self):
        # impedir cambios por POST: siempre conservar el del usuario
        return self.instance.email or resolve_user_email(self.instance)

    def save(self, commit=True):
        obj = super().save(commit=False)
        # blindaje: nunca permitir que cambie el email desde el form
        obj.email = self.instance.email or resolve_user_email(self.instance)
        if commit:
            obj.save()
        return obj
