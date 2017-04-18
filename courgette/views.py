from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template import loader
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.generic.edit import FormView

from django import forms
from django.db.models import Q


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email"), max_length=160)


#########################################################
#               PASSWORD RESET METHOD                   #
#########################################################


class ResetPasswordRequestView(FormView):
    template_name = "registration/password_reset_form.html"
    success_url = '/password_reset_done/'
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]
        if self.validate_email_address(data) is True:
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        'email': user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'courgette.com',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                subject_template = 'registration/password_reset_subject.txt'
                email_template_name = 'registration/password_reset_email.html'
                subject = loader.render_to_string(subject_template, c)
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, 'backend@courgette.com', [user.email], fail_silently=False)
            result = self.form_valid(form)
            messages.success(request, "An email has been sent to " + data + ". Please check its inbox.")
            return result
        result = self.form_invalid(form)
        messages.error(request, "No user is associated with this email")
        return result


class SetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': "The two password fields don't match!"
    }
    new_password1 = forms.CharField(label=("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"), widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2


class PasswordResetConfirmView(FormView):
    template_name = "registration/password_reset_confirm.html"
    success_url = '/password_reset_complete/'
    form_class = SetPasswordForm

    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None:
            print(user)
            print(token)
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(request, 'The password link is no longer valid.')
            return self.form_invalid(form)
