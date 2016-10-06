from rest_framework import generics, permissions, status
from rest_framework.response import Response

from django.core.mail import EmailMessage
from django.conf import settings

# Create your views here.
from apps.api.models import Feed
from apps.api.v1.feedback.forms import FeedbackForm
from apps.api.v1.feedback.serializers import FeedbackSerializer


class FeedbackSubmit(generics.GenericAPIView):
    """
    list all feedbacks
    
    ## Reading
    You can't read using this endpoint.
    
    
    ## Publishing
    ### Permissions
    * Anyone can create using this endpoint. Authenticated users will have
      emails logged for follow-up if need be.
    
    ### Fields
    Parameter  | Description                        | Type
    ---------- | ---------------------------------- | ---------- 
    `body`     | feedback body                      | _string_
        
    ### Response
    If successful, **_true_**, else an error message.
    
    
    ## Deleting
    You can't delete using this endpoint.
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    permission_classes = (permissions.AllowAny,)
    queryset = Feed.objects.all()
    serializer_class = FeedbackSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            # Create FeedbackForm with the serializer
            feedback_form = FeedbackForm(data=serializer.data)

            if feedback_form.is_valid():
                feedback = feedback_form.save()
                if self.request.user.is_authenticated():
                    feedback.email = self.request.user.email
                    feedback.save()

                # email admins
                cd = feedback_form.cleaned_data
                body = "Email: " + feedback.email + \
                       "\n\nMessage:\n" + cd['body']
                subject = "Email from mufield.com feedback form"
                email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL,
                                     ["895196292@qq.com"],
                                     headers={'Reply-To': feedback.email})

                email.send(fail_silently=True)

                # Return the success message with OK HTTP status
                return Response({
                    'detail': True
                })

            else:
                return Response(feedback_form.errors,
                                status=status.HTTP_400_BAD_REQUEST)


        # coming this far means there likely was a problem
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
