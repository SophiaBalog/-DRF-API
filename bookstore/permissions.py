from rest_framework.permissions import SAFE_METHODS, BasePermission

EDU_DOMAIN = "edu.ua"


def has_edu_email(user):
    domain = (user.email or "").rpartition("@")[2].strip().lower()
    return domain == EDU_DOMAIN or domain.endswith("." + EDU_DOMAIN)


class IsEduUserOrReadOnly(BasePermission):
    message = "Змінювати книги можуть лише користувачі з поштою в домені .edu.ua."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and has_edu_email(user))