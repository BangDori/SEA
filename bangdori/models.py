import datetime
from io import StringIO

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
# AbstractUser를 상속받는 모델로 변경
class CustomerUser(AbstractUser):
    """
    CustomerUser : 사용자 정보를 저장하는 Model

    Parameters
    ----------
    email : CharField
        이메일
    birthday : DateField
        생일
    phone : CharField
        전화번호
    nickname : CharField
        닉네임
    blocked_at : DateField
        (예정 : is_active 필드와 함께 작동) 사용자가 비활성화된 날짜를 알려줌
    corp_num : CharField
        사업자 등록번호
    """

    email = models.CharField(
        max_length=30, db_column='email', verbose_name='email', blank=True)
    birthday = models.DateField(
        default=datetime.MINYEAR, db_column='birth', verbose_name='birth')
    phone = models.CharField(
        max_length=30, db_column='phone', verbose_name='phone')

    def __str__(self):
        return self.username


class Authentication(models.Model):
    phone_number = models.CharField('휴대폰 번호', max_length=30)
    auth_number = models.CharField('인증번호', max_length=30)

    class Meta:
        db_table = 'authentications'  # DB 테이블명
        verbose_name_plural = "휴대폰인증 관리 페이지"  # Admin 페이지에서 나타나는 설명


class Article(models.Model):
    """
    Article : 게시물 정보를 저장하는 Model

    Parameters
    ----------
    id : AutoField
        Integer 형식의 SeqID를 나타내는 PK
    title : CharField
        게시글 제목
    writer : ForeignKey
        작성자, CustomerUser의 username를 FK로 함
        1:N 특성을 가지므로, 계정 삭제시 같이 삭제될 수 있는 CASCADE 특성 사용
    content : TextField
        게시글 내용
    date :
        글 작성 일자, auto_now_add 파라미터를 True로 하여 INSERT시 자동으로 날짜가 생성되는 옵션 사용
    views : PositiveIntegerField
        조회수, 음수가 없으므로 unsigned int 사용
    upvote : PositiveIntegerField
        추천수, 조회수와 마찬가지의 형식 사용
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='제목')
    writer = models.ForeignKey(
        'CustomerUser', on_delete=models.CASCADE, verbose_name='글쓴이')
    content = models.TextField(verbose_name='내용')
    date = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    views = models.PositiveIntegerField(default=0, verbose_name='조회')
    upvote = models.PositiveIntegerField(default=0, verbose_name='추천')

    def __str__(self):
        # __str__ 오버라이드로 제목만 표시
        return self.title

    class Meta:
        # Meta 클래스 오버라이드로 상세 내용 지정 (Form을 위함)
        abstract = True


class Comment(models.Model):
    # Article과 유사하게 abstract로 선언후 필요 Article에만 사용
    content = models.TextField()
    writer = models.TextField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DabangArticle(Article):
    """
    다방 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_dabang'
        verbose_name = '다방'
        verbose_name_plural = '다방'


class SuccessionArticle(Article):
    """
    승계 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_succession'
        verbose_name = '승계'
        verbose_name_plural = '승계'


class SuccessionComment(Comment):
    """
    승계 댓글로, Comment를 상속받음
    """
    class Meta:
        db_table = 'comment_succession'
        verbose_name = '승계댓글'
        verbose_name_plural = '승계댓글'


class EssentialsArticle(Article):
    """
    필수템 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_essentials'
        verbose_name = '필수템'
        verbose_name_plural = '필수템'


class GroupArticle(Article):
    """
    공동구매 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_group'
        verbose_name = '공동구매'
        verbose_name_plural = '공동구매'


class BoardArticle(Article):
    """
    자유 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_board'
        verbose_name = '자유'
        verbose_name_plural = '자유'


class BoardComment(Comment):
    """
    자유 게시판 댓글로, Comment를 상속받음
    """

    class Meta:
        db_table = 'comment_board'
        verbose_name = '자유댓글'
        verbose_name_plural = '자유댓글'


class NoticeArticle(Article):
    """
    공지 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_notice'
        verbose_name = '공지'
        verbose_name_plural = '공지'


class ContactArticle(Article):
    """
    자유 게시판으로, Article을 상속받음
    """

    class Meta:
        db_table = 'article_contact'
        verbose_name = '문의'
        verbose_name_plural = '문의'


class Address(models.Model):
    pass