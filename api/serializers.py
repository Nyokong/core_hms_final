from rest_framework import serializers

from .models import FeedbackMessage


# feedback serializer goes here
class FeedbackMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackMessage
        fields = ['user', 'message', 'timestamp']

    def create(self, validated_data):
        
        msg = FeedbackMessage(
            user=self.context['request'].user, # logged in user
            message=validated_data['message'], # the message
            timestamp=validated_data['timestamp'] # the time of posting
        )

        # save the video if is succesful
        msg.save()
        # after all return user
        return msg

    