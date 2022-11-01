import json
import os
import random
import time

import requests
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView
from dotenv import load_dotenv

from project.settings import MAX_ARTICLES
from .models import *
from .utils import make_signature, getModelByName

load_dotenv()


# Create your views here.

def goIndex(request):
    return redirect('index')


def index(request):
    context = {}
    """
    로그인 정보는 Session에 기록되도록 설정되어 있음.
    dict 형식으로 request 전달 비활성화
    """
    # logged_user = request.session.get('user')
    # print(logged_user)
    # logged_user = {}
    # if logged_user:
    #     user = CustomerUser.objects.get(username=username)
    #     username['username'] = user.username
    #     username['user_email'] = user.email
    #     username['user_birth'] = user.birthday
    #     username['user_phone'] = user.phone
    #     username['user_logged_in'] = TRUE

    return render(request, 'index.html', {})


def login(request):
    # 기본이 POST로 수정
    if request.method == "POST":
        context = {}
        # AuthenticationForm으로부터 인증 Form을 받아옴
        form = AuthenticationForm(request=request, data=request.POST)

        if form.is_valid():
            # cleaned_data 형식으로 아이디와 비밀번호를 가져옴
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Django의 auth 클래스를 사용해 로그인
            user = auth.authenticate(
                request=request, username=username, password=password)
            # 해당하는 유저가 존재해서 로그인이 가능한 경우
            if user is not None:
                auth.login(request, user)
                return redirect('/index')

        """
        DB에서 Filter를 이용하지 않고, auth 클래스를 이용하여 로그인하도록 수정함
        오류 메시지는 아직 구현되지 않음
        """
        # if not (username and password):
        #     context['error'] = "빈칸없이 입력해주세요."
        # else:
        #     if CustomerUser.objects.filter(username=username):
        #         user = CustomerUser.objects.get(username=username)
        #         if check_password(password, user.password):
        #             request.session['user'] = user.username
        #             return redirect('/index')
        #         else:
        #             context['error'] = "해당 회원정보가 존재하지 않습니다."
        #     else:
        #         context['error'] = "해당 회원정보가 존재하지 않습니다."
    else:
        return render(request, 'login.html')

    return render(request, 'login.html', context)


def logout(request):
    # del 방식을 이용하지 않고, auth에서 제공하는 메서드를 이용
    auth.logout(request)
    return redirect('/index')


def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        # register로 POST 요청이 들어오면, 새로운 User를 생성하는 절차
        context = {}

        username = request.POST.get('register_username', None)
        password = request.POST.get('register_user_pwd', None)
        password2 = request.POST.get('register_user_repwd', None)
        email_id = request.POST.get('register_user_email_id', None)
        email_net = request.POST.get('register_user_email', None)
        year = request.POST.get('register_user_year', None)
        month = request.POST.get('register_user_month', None)
        day = request.POST.get('register_user_day', None)
        phone = request.POST.get('register_user_phone', None)

        # 중복 확인 구현할 것
        if CustomerUser.objects.filter(username=username).exists():
            context['error'] = "사용할 수 없는 ID입니다."

        if password != password2:
            context['error'] = "비밀번호가 다릅니다."
        elif not (username and password and password2 and email_id and email_net
                  and year and month and day and phone):
            context['error'] = "빈칸없이 입력해주세요."
        else:
            user = CustomerUser.objects.create_user(username=username,
                                                    password=password2,
                                                    email=f'{email_id}@{email_net}',
                                                    birthday=f'{year}-{month}-{day}',
                                                    phone=phone)
            auth.login(request, user)
            return redirect('/')

        return render(request, 'register.html', context)


def id_check(request):
    username = request.GET.get('register_username')
    if CustomerUser.objects.filter(username=username).exists():
        result = {
            'result': 'success',
            # 'data' : model_to_dict(user)  # console에서 확인
            'data': "exist"
        }
    else:
        result = {
            'result': 'success',
            # 'data' : model_to_dict(user)  # console에서 확인
            'data': "not exist"
        }
    # try:
    #     user = CustomerUser.objects.get(username=username)
    # except:
    #     user = None
    # if user is None:
    #     result = "not exist"
    # else:
    #     result = "exist"
    # context = {'result':result}
    return JsonResponse(result)


class DetailView(DetailView):
    model = CustomerUser
    context_object_name = 'target_user'
    template_name = 'view.html'
    print(type(model))
    print(type(context_object_name))
    print(type(template_name))


def dabang(request):
    return render(request, 'dabang.html')


def succession(request):
    return render(request, 'succession.html')


def essentials(request):
    return render(request, 'essentials.html')


def group(request):
    return render(request, 'group.html')


def board(request, name):
    """
    board : 게시판 목록을 보여주는 view
    """

    # 페이지에 넘겨줄 Context
    context = {}

    # 게시판 내용 불러올 Article 객체
    articles = getModelByName(name)

    # 페이지 정보 전달
    # context['name'] : 페이지가 표시되는 한글 이름
    context['name'] = articles._meta.verbose_name
    # context['url'] : 페이지에서 url로 전달받은 이름
    context['url'] = name

    # 모든 글 가져옴, 날짜 내림차순으로 조회
    articles = articles.objects.all().order_by('-date')
    # Paginator 사용
    paginator = Paginator(articles, MAX_ARTICLES)
    # GET 요청이 들어오면 page 파라미터를 읽어옴
    page = int(request.GET.get('page', 1))

    # 현재 페이지에 맞는 게시물 목록을 Context로 넘겨줌
    context['articles'] = paginator.get_page(page)

    return render(request, 'board.html', context)


def notice(request):
    return render(request, 'notice.html')


def contact(request):
    return render(request, 'contact.html')


def article(request, name, pk):
    """
    article : 게시글 내용을 보여주는 view
    """

    context = {}

    # 게시글 정보 불러옴
    article = getModelByName(name)
    article = article.objects.all().get(id=pk)

    # 조회수 올림
    article.views = article.views + 1
    article.save()

    # Context에 전달
    context['article'] = article
    context['url'] = name

    return render(request, 'article.html', context)


def update(request, name, pk):
    """
    update : 게시글 update하는 view
    """
    user = request.user
    Article = getModelByName(name)
    article = Article.objects.all().get(id=pk)
    if article.writer != user:
        return redirect('article', name=name, pk=pk)
    if request.method == "POST":
        # 게시글 수정
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.save()
        return redirect('article', name=name, pk=pk)

    context = {}
    context['title'] = article.title
    context['content'] = article.content
    return render(request, 'update.html', context)


def write(request, name):
    """
    write : 게시글을 작성하는 view
    """
    # 현재 로그인된 사용자의 정보를 가져옴
    user = request.user

    if request.method == "POST":
        # 현재 게시판에 맞는 모델을 가져옴
        article = getModelByName(name)

        # 게시글 작성
        article = article(title=request.POST.get('title'),
                          writer=CustomerUser.objects.get(username=user),
                          content=request.POST.get('content'))

        # 게시글 저장

        article.save()
        # 게시판으로 다시 돌아감
        return redirect('board', name=name)

    return render(request, 'write.html')


def findID(request):
    return render(request, 'findID.html')


def SMS(request):
    return render(request, 'temp_sms.html')


def SMSPW(request):
    return render(request, 'temp_smsPW.html')


def findPW1(request):
    return render(request, 'findPW1.html')


def findPW2(request):
    return render(request, 'findPW2.html')


class SmsSendView(View):
    def send_sms(self, phone_number, auth_number):
        timestamp = str(int(time.time() * 1000))
        headers = {
            'Content-Type': "application/json; charset=UTF-8",
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': os.getenv('ncloud_private_Accesskey'),
            'x-ncp-apigw-signature-v2': make_signature(timestamp)
        }
        body = {
            "type": "SMS",
            "contentType": "COMM",
            # 사전에 등록해놓은 발신용 번호 입력, 타 번호 입력시 오류
            "from": os.getenv('call_number'),
            "content": f"[강병준 씹새야:{auth_number}]",  # 메세지를 이쁘게 꾸며보자
            "messages": [{"to": f"{phone_number}"}]
        }
        body = json.dumps(body)
        requests.post(
            'https://sens.apigw.ntruss.com/sms/v2/services/ncp:sms:kr:292652557635:sms_auth/messages', headers=headers,
            data=body)

    def post(self, request):
        # data = json.loads(request.body)
        try:
            input_mobile_num = request.POST['phone_number']
            print(input_mobile_num)
            auth_num = random.randint(10000, 100000)  # 랜덤숫자 생성, 5자리로 계획하였다.
            auth_mobile = Authentication.objects.get(
                phone_number=input_mobile_num)
            auth_mobile.auth_number = auth_num
            auth_mobile.save()
            self.send_sms(
                phone_number=input_mobile_num, auth_number=auth_num)
            return JsonResponse({'message': 'Complete 발송완료'}, status=200)
        except Authentication.DoesNotExist:  # 인증요청번호 미 존재 시 DB 입력 로직 작성
            Authentication.objects.create(
                phone_number=input_mobile_num,
                auth_number=auth_num,
            ).save()
            self.send_sms(phone_number=input_mobile_num, auth_number=auth_num)
            return JsonResponse({'message': '인증번호 발송 및 DB 입력완료'}, status=200)


class SmsVerifyView(View):
    def post(self, request):
        input_mobile_num = request.POST['phone_number']
        message = request.POST['message_number']
        stragety = request.POST['stragety']
        if(stragety == 'findID'):
            auth_mobile = Authentication.objects.get(
                phone_number=input_mobile_num)
            if (auth_mobile.auth_number == message):
                user = CustomerUser.objects.get(
                    phone=input_mobile_num)
                if (user):
                    auth_mobile.delete()
                    return JsonResponse({'message': str(user.username)}, status=200)
                else:
                    return JsonResponse({'message': 'Not User!'}, status=200)
            else:
                return JsonResponse({'message': 'Not Correct Number!'}, status=200)


class kakaologin(View):
    def get(self, request):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        redirect_uri = "http://localhost:8000/login/kakao/callback/"
        client_id = "061401748822539ecf6d032fcc459c14"

        return redirect(
            f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}")


class kakaocallback(View):
    def get(self, request):
        data = {
            "grant_type": "authorization_code",
            "client_id": "061401748822539ecf6d032fcc459c14",
            "redirection_uri": "http://localhost:8000/login/kakao",
            "code": request.GET["code"]
        }
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        access_token = requests.post(kakao_token_api, data=data).json()[
            "access_token"]

        kakao_user_api = "https://kapi.kakao.com/v2/user/me"
        header = {"Authorization": f"Bearer ${access_token}"}
        json = requests.get(kakao_user_api, headers=header).json()
        try:
            user = CustomerUser.objects.all().get(provider=json['id'])
        except CustomerUser.DoesNotExist:
            user = None
        if user is not None:
            auth.login(request, user)
            return redirect('/index')
        user = CustomerUser.objects.create_user(provider=json['id'],
                                                email=json['kakao_account']['email'],
                                                username=json['kakao_account']['profile']['nickname'],
                                                )
        user.save()
        auth.login(request, user)
        return redirect('/index')


class googlelogin(View):
    def get(self, request):
        google_api = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code"
        redirect_uri = "http://localhost:8000/login/google/callback/"
        client_id = "423096054112-5hoh9i9p6i9bppac2cs3dea30cc5jvr6.apps.googleusercontent.com"
        scope = "https://www.googleapis.com/auth/userinfo.email " + \
                "https://www.googleapis.com/auth/userinfo.profile"

        return redirect(
            f"{google_api}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}")


class googlecallback(View):
    def get(self, request):
        google_token_api = 'https://oauth2.googleapis.com/token'
        # secret key 일부러 빼놓음.
        data = {
            "code": request.GET['code'],
            "client_id": "423096054112-5hoh9i9p6i9bppac2cs3dea30cc5jvr6.apps.googleusercontent.com",
            "redirect_uri": "http://localhost:8000/login/google/callback/",
            "client_secret": "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",
            "grant_type": "authorization_code",
        }
        access_token = requests.post(google_token_api, data=data).json()[
            "access_token"]
        google_user_api = "https://www.googleapis.com/oauth2/v3/userinfo"
        json = requests.get(google_user_api,
                            params={"access_token": access_token}).json()
        # 받아오는 숫자가 16자리로 너무 커서 SQL에서 변환 도중 오류가 남

        try:
            user = CustomerUser.objects.all().get(provider=json['sub'])
        except CustomerUser.DoesNotExist:
            user = None
        if user is not None:
            auth.login(request, user)
            return redirect('/index')

        user = CustomerUser.objects.create_user(provider=json['sub'],
                                                email=json['email'],
                                                username=json['name'],
                                                )
        auth.login(request, user)
        return redirect('/index')


class naverlogin(View):
    def get(self, request):
        naver_api = "https://nid.naver.com/oauth2.0/authorize?response_type=code"
        redirect_uri = "http://localhost:8000/login/naver/callback/"
        client_id = "wbvRsxRzlRkolqqiMZq1"
        state = "bangdori"
        return redirect(
            f"{naver_api}&client_id={client_id}&redirect_uri={redirect_uri}&state={state}")


class navercallback(View):
    def get(self, request):
        naver_token_api = "https://nid.naver.com/oauth2.0/token"
        data = {
            "code": request.GET['code'],
            "client_id": "wbvRsxRzlRkolqqiMZq1",
            "redirect_uri": "http://localhost:8000/login/naver/callback/",
            "client_secret": "ff_Bbw3Iba",
            "state": "bandori",
            "grant_type": "authorization_code",
        }
        access_token = requests.post(naver_token_api, data=data).json()[
            'access_token']
        naver_user_api = "https://openapi.naver.com/v1/nid/me"
        header = {"Authorization": f"Bearer ${access_token}"}

        json = requests.get(naver_user_api,
                            params={"access_token": access_token}).json()['response']
        uid = int(json['mobile_e164'][1:])
        try:
            user = CustomerUser.objects.all().get(provider=uid)
        except CustomerUser.DoesNotExist:
            user = None
        if user is not None:
            auth.login(request, user)
            return redirect('/index')
        user = CustomerUser.objects.create_user(provider=uid,
                                                email=json['email'],
                                                birthday=json['birthyear'] +
                                                '-' + json['birthday'],
                                                username=json['nickname'],
                                                phone=json['mobile'],
                                                )
        auth.login(request, user)
        return redirect('/index')

# class address(View):
#     def get(self, request):
#         if request.user.is_anonymous:
#             return redirect(reverse('index'))

#         return render(request, 'address.html')

#     def post(self, request):
#         addr = Address()
#         try:
#             addr.postcode = int(request.POST.get('postcode'))
#         except:
#             pass

#         addr.road = request.POST.get('road')
#         addr.lot = request.POST.get('lot')
#         addr.detail = request.POST.get('detail')
#         addr.extra = request.POST.get('extra')
#         addr.city = request.POST.get('sido')
#         addr.state = request.POST.get('sigungu')
#         addr.road_name = request.POST.get('roadname')
#         addr.lat = float(request.POST.get('lat'))
#         addr.lng = float(request.POST.get('lng'))

#         user = request.user


#         return render(request, 'address.html')
