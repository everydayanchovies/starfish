from django.core.validators import validate_email
from django.forms import Form, CharField


class ChangePasswordForm(Form):
    newpassword = CharField(max_length=40, required=False)
    confirmnewpassword = CharField(max_length=40, required=False)

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        if cleaned_data:
            newpassword = cleaned_data["newpassword"]
            confirmnewpassword = cleaned_data["confirmnewpassword"]
            if confirmnewpassword != newpassword:
                self.errors["confirmnewpassword"] = "Both password must be equal!"
            elif 0 < len(cleaned_data["newpassword"]) < 8:
                self.errors["newpassword"] = "Password must contain at least 8 characters"
        return cleaned_data


class ChangeEmailForm(Form):
    newemail = CharField(validators=[validate_email], required=False)
    confirmnewemail = CharField(validators=[validate_email], required=False)

    def clean(self):
        cleaned_data = super(ChangeEmailForm, self).clean()
        if cleaned_data:
            newemail = cleaned_data["newemail"]
            confirmnewemail = cleaned_data["confirmnewemail"]
            if confirmnewemail != newemail:
                self.errors["confirmnewemail"] = "Both email addresses must be equal!"
        return cleaned_data
