# coding:utf-8
'''
Created on 2017年5月8日

@author: hepeng
'''
import base64
from rest_framework import serializers, validators
from .models import ChatMessageModel, URobotModel, ChatRoomModel,\
IntoChatRoomMessageModel, IntoChatRoom, DropOutChatRoom, MemberInfo

def decode_base64(chars):
    if type(chars) is unicode:
        chars = chars.encode('utf8')
    return base64.urlsafe_b64decode(chars)

class ChatMessageSerializer(serializers.ModelSerializer):
    dtMsgTime = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False)
    def create(self, validated_data):
        if int(validated_data['nMsgType']) == 2001:
            content = decode_base64(validated_data['vcContent']).decode('utf-8')
            content = content.strip('\n')
            validated_data['vcContent'] = content
        return super(ChatMessageSerializer, self).create(validated_data)
    class Meta:
        model = ChatMessageModel
        fields = '__all__'
        
class URobotSerializer(serializers.ModelSerializer):
    class Meta:
        model = URobotModel
        fields = '__all__'
        
class ChatRoomSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        name = decode_base64(validated_data['vcBase64Name']).decode('utf-8')
        name = name.strip('\n')
        validated_data['vcName'] = name
        return super(ChatRoomSerializer, self).create(validated_data)
    class Meta:
        model = ChatRoomModel
        fields = '__all__'
        
class IntoChatRoomMessageSerializer(serializers.ModelSerializer):
    dtCreateDate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    def create(self, validated_data):
        groupname = decode_base64(validated_data['vcBase64Name']).decode('utf-8')
        nickname = decode_base64(validated_data['vcBase64NickName']).decode('utf-8')
        groupname = groupname.strip('\n')
        nickname = nickname.strip('\n')
        validated_data['vcName'] = groupname
        validated_data['vcNickName'] = nickname
        return super(IntoChatRoomMessageSerializer, self).create(validated_data)
    class Meta:
        model = IntoChatRoomMessageModel
        fields = '__all__'
        
class IntoChatRoomSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        nickname = decode_base64(validated_data['vcBase64NickName']).decode('utf-8')
        nickname = nickname.strip('\n')
        validated_data['vcNickName'] = nickname
        return super(IntoChatRoomSerializer, self).create(validated_data)
    class Meta:
        model = IntoChatRoom
        fields = '__all__'
        
class DropOutChatRoomSerializer(serializers.ModelSerializer):
    dtCreateDate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    class Meta:
        model = DropOutChatRoom
        fields = '__all__'

class MemberInfoSerializer(serializers.ModelSerializer):
    dtLastMsgDate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', input_formats=('%Y/%m/%d %H:%M:%S', ''), allow_null=True)
    dtCreateDate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', input_formats=('%Y/%m/%d %H:%M:%S', ''), allow_null=True)
    def create(self, validated_data):
        nickname = decode_base64(validated_data['vcBase64NickName']).decode('utf-8')
        nickname = nickname.strip('\n')
        validated_data['vcNickName'] = nickname          
        return super(MemberInfoSerializer, self).create(validated_data)

    def run_validators(self, value):
        for validator in self.validators:
            if isinstance(validator, validators.UniqueTogetherValidator):
                self.validators.remove(validator)
        super(MemberInfoSerializer, self).run_validators(value)

    def create(self, validated_data):
        instance, _ = MemberInfo.objects.get_or_create(**validated_data)
        return instance

    class Meta:
        model = MemberInfo
        fields ='__all__'