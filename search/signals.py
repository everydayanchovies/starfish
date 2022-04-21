import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import Signal, receiver

from search.models import Person

# providing args: author, title, tags
unknown_tag_signal = Signal()

logger = logging.getLogger('search')


@receiver(unknown_tag_signal)
def unknown_tag_callback(sender, **kwargs):
    author = Person.objects.get(pk=kwargs['author'])
    title = kwargs['title']
    unknown_tags = kwargs['tags']
    message = "Dear moderator,\n\n" + \
              u"{person} created an item '{title}' ".format(person=author.name,
                                                            title=title) + \
              "and tried to add the following nonexisting tags:\n\n" + \
              "Tokens: " + ','.join(unknown_tags['token']) + "\n" + \
              "Persons: " + ','.join(unknown_tags['person']) + "\n" + \
              "Literals: " + ','.join(unknown_tags['literal']) + "\n\n" + \
              "It is up to you to determine whether these tags should " + \
              "exist and add them to both the system and this item." + \
              "\n\nThis message was generated automatically."
    logger.debug(message)
    subject = u'[Starfish] User {person} uses unknown tags'.format(
        person=author.name)
    from_email = "notifications@%s" % (settings.HOSTNAME,)
    msg = EmailMultiAlternatives(subject, message, from_email,
                                 to=settings.ADMIN_NOTIFICATION_EMAIL)
    msg.send(fail_silently=True)
