from django.db import models


class Lang(models.TextChoices):
    RU = 'ru'
    EN = 'en'


class BotUser(models.Model):
    users = models.Manager()
    chat_id = models.IntegerField(unique=True)
    lang = models.CharField(max_length=2, choices=Lang.choices,
                            verbose_name='Язык')
    first_name = models.CharField(max_length=255,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=255, null=True,
                                 verbose_name='Фамилия')
    username = models.CharField(max_length=255, null=True,
                                verbose_name='Ник')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Task(models.Model):
    class Type(models.IntegerChoices):
        TRUTH = 1, 'Правда'
        DARE = 2, 'Действие'

    tasks = models.Manager()
    type = models.IntegerField(choices=Type.choices, verbose_name='Тип')
    body_ru = models.TextField(verbose_name='Текст на русском')
    body_en = models.TextField(verbose_name='Текст на английском')

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def get_body(self, lang):
        return getattr(self, f'body_{lang}')


class Chat(models.Model):
    chats = models.Manager()
    chat_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, verbose_name='Название')
    lang = models.CharField(max_length=2, choices=Lang.choices,
                            verbose_name='Язык')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Game(models.Model):
    games = models.Manager()
    chat = models.OneToOneField(to=Chat,
                                on_delete=models.CASCADE,
                                related_name='game',
                                verbose_name='Игра')
    current_player = models.ForeignKey(
        to=BotUser,
        on_delete=models.CASCADE,
        null=True,
    )
    message_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'


class GameParticipant(models.Model):
    participants = models.Manager()
    user = models.ForeignKey(
        to=BotUser,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Пользователь',
    )
    game = models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Игра',
    )

    class Meta:
        verbose_name = 'Участник игры'
        verbose_name_plural = 'Участники игры'


class GamePlayer(models.Model):
    players = models.Manager()
    user = models.ForeignKey(
        to=BotUser,
        on_delete=models.CASCADE,
        related_name='players',
        verbose_name='Пользователь',
    )
    game = models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        related_name='players',
        verbose_name='Игра',
    )
    task = models.ForeignKey(
        to=Task,
        on_delete=models.CASCADE,
        related_name='players',
        verbose_name='Задание',
        null=True,
    )

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'
        unique_together = [('user', 'game')]


class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.MESSAGE)


class KeyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.KEY)


class SmileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.SMILE)


class Template(models.Model):
    class Type(models.IntegerChoices):
        MESSAGE = 1
        KEY = 2
        SMILE = 3

    templates = models.Manager()
    messages = MessageManager()
    keys = KeyManager()
    smiles = SmileManager()

    type = models.IntegerField(choices=Type.choices, verbose_name='Тип')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    body_ru = models.TextField(verbose_name='На русском')
    body_en = models.TextField(verbose_name='На английском')

    def gettext(self, lang):
        body = getattr(self, f'body_{lang}')
        if self.type != Template.Type.MESSAGE:
            body = body.replace('<p>', '')
            body = body.replace('</p>', '')

        return body

    def getall(self):
        return (self.gettext(Lang.EN), self.gettext(Lang.RU))

    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны'
