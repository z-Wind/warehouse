"""lotusNotes email backend class."""

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address

import uuid

from win32com.client import DispatchEx
import pywintypes # for exception

class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the lotusNotes network connection.
    """
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.username = settings.EMAIL_HOST_USER if username is None else username
        self.password = settings.EMAIL_HOST_PASSWORD if password is None else password
        self.document = None

    def open(self):
        """
        Ensures we have a document to the email server. Returns whether or
        not a new document was required (True or False).
        """
        if self.document:
            # Nothing to do if the document is already open.
            return False
        
        mailServer =  self.host
        mailPath = self.username
        mailPassword = self.password
        # Connect
        notesSession = DispatchEx('Lotus.NotesSession')
        try:
            notesSession.Initialize(mailPassword)
            notesDatabase = notesSession.GetDatabase(mailServer, mailPath)
            document = notesDatabase.CreateDocument()
            self.document = document
            return True
        except pywintypes.com_error:
            raise Exception('Cannot access mail using %s on %s' % (mailPath, mailServer))

    def close(self):
        """Closes the connection to the email server."""
        pass

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return

        new_conn_created = self.open()
        if not self.document:
            # We failed silently on open().
            # Trying to send would be pointless.
            return
        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        if new_conn_created:
            self.close()
            
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False

        sendto = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        message = email_message.message()
        subject = email_message.subject
        
        self.document.ReplaceItemValue("Form","Memo")
        self.document.ReplaceItemValue("Subject", subject)

        # assign random uid because sometimes Lotus Notes tries to reuse the same one
        uid = str(uuid.uuid4().hex)
        self.document.ReplaceItemValue('UNIVERSALID', uid)

        # "SendTo" MUST be populated otherwise you get this error:
        # 'No recipient list for Send operation'
        self.document.ReplaceItemValue("SendTo", sendto)

        # body
        body = self.document.CreateRichTextItem("Body")
        body.AppendText(message)

        # save in `Sent` view; default is False
        self.document.SaveMessageOnSend = True
        self.document.Send(False)
        
        return True
