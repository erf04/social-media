from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from api.models import Group,PrivateChat,User,Follower, Message
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,parser_classes
from .serializers import GroupSerializer,PrivateChatSerializer
from .models import *
from django.shortcuts import get_object_or_404
from api.permissions import IsOwnerOrReadOnly
from rest_framework import permissions,generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime
from .serializers import CompleteUserSerializer
from itertools import chain
import markdown2

class GroupApiView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request:Request):
        groups=Group.objects.filter(participants=request.user)
        serialized=GroupSerializer(groups,many=True)
        return Response(serialized.data,status=status.HTTP_200_OK)

    def post(self,request:Request): 
        group_name=request.data['group_name']
        image=request.data['image']
        
        if image!="null":
            group=Group.objects.create(name=group_name,creator=request.user,image=image,creation_date=datetime.now())
        else:
            group=Group.objects.create(name=group_name,creator=request.user,creation_date=datetime.now())

        group.participants.add(request.user)
        group.save()
        serialized=GroupSerializer(group, many=False)
        return Response(serialized.data,status=status.HTTP_201_CREATED)

    


class PrivateRoomView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request:Request):
        private_chats=PrivateChat.objects.filter(Q(creator=request.user) | Q(the_other=request.user))
        serialized=PrivateChatSerializer(private_chats,many=True)
        return Response(serialized.data,status=status.HTTP_200_OK)

    def post(self,request:Request):
        other_id=request.data["other_id"]
        the_other=User.objects.get(pk=other_id)
        private_chat,created=PrivateChat.objects.get_or_create(creator=request.user,the_other=the_other)
        serialized=PrivateChatSerializer(private_chat,many=False)
        if created:
            return Response(serialized.data,status=status.HTTP_201_CREATED)
        return Response(serialized.data,status=status.HTTP_200_OK)
    

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def add_participants_to_group(request:Request):
    participants_id_list=request.data["participants"]
    group_id=request.data["group_id"]
    print(f"ids:{participants_id_list}")
    myuser=request.user
    # last_group=Group.objects.filter(creator=myuser).last()
    group=Group.objects.get(pk=group_id)
    for id in  participants_id_list:
        user=User.objects.get(pk=id)
        group.participants.add(user)

    serialized=GroupSerializer(group,many=False)
    return Response(serialized.data,status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_followers_and_followings(request:Request):
    user:User=request.user

    followers=User.objects.filter(followings__followed=user)
    followings=User.objects.filter(followers__follower=user)
    users=followers | followings
    serializer=CompleteUserSerializer(users,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def filter_groups(request:Request):
    key=request.data["key"]
    groups=Group.objects.filter(participants=request.user).filter(name__contains=key.lower())
    serialized=GroupSerializer(groups,many=True)
    return Response(serialized.data,status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def filter_pv(request:Request):
    key=request.data["key"]
    user=request.user
    private_chats1=PrivateChat.objects.filter(creator=request.user).filter(the_other__username__contains=key.lower())
    private_chats2=PrivateChat.objects.filter(the_other=request.user).filter(creator__username__contains=key.lower())
    private_chats=private_chats1 | private_chats2
    serialized=PrivateChatSerializer(private_chats,many=True)
    return Response(serialized.data,status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def delete_message(request):
    message_id = request.data["message_id"]
    message = Message.objects.get(pk=message_id).delete()
    return Response({"message": "deleted"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def websocket_docs(request:Request):
    html_content = markdown2.markdown(documentation)
    return render(request,"websocket_swagger.html",{
        "documentation":html_content
    })
