# ADMIN
ADMIN_MENU = """ADMIN MENU"""
ADMIN_NOTIFY = """<blockquote>Yangi foydalanuvchi !</blockquote>"""
ADMIN_NOTE = \
"""Xabarga e'tibor berishingiz kerak, chunki foydalanuvchi
bazaga saqlangan!"""


# USER
#### NEW USER
WELCOME = \
"""Assalomu alaykum, Xush kelibsiz.
Ro'yxatdan o'tish usulini tanlang!"""

#### STUDENT
STUDENT_WELCOME = """Assalomu alaykum, hurmatli o'quvchi !"""
STUDENT = """O'quvchi"""
STUDENT_ATTENDANCE = """O'quvchilar davomatini belgilash"""
STUDENT_PAYMENTS = """O'quvchilar to'lovlarini belgilash"""
STUDENT_PAYMENT_DATE_ERROR = """To'lovni yangilash uchun 1 oy to'lgan bo'lishi kerak!"""
STUDENT_PAYMENT_DATE_UPDATE = """Oxirgi to'lov sanasi o'zgartirildi va ma'lumot o'quvchiga jo'natildi!"""
STUDENT_ATTENDANCE_INFOS_SENDED = """Davomat statusi o'quvchilarga yuborildi!"""
STUDENT_SELECT = """O'quvchi sifatida ro'yxatdan o'tish"""
STUDENT_GROUPS = """Guruhlarim"""
STUDENT_RESULTS = """Natijalarim"""
STUDENT_SUBJECTS = """Fanlarim"""
STUDENT_FULLNAME = """Ism-familiyangizni kiriting: """
STUDENT_SELECT_SUBJECT = """O'qimoqchi bo'lgan faningiz: """
STUDENT_SELECT_GROUP = """O'qimoqchi bo'lgan guruhingiz: """
STUDENT_SEND_DATAS = """Ma'lumotlarni o'qituvchiga yuborish"""
STUDENT_COUNT_ERROR = """Bu guruhga hali o'quvchilar qo'shilmagan!"""

STUDENT_ATTENDANCE_EXIST_STATUS = '✅'
STUDENT_ATTENDANCE_NOT_EXIST_STATUS = '❌'

STUDENT_PHONE_ASK = \
"""Telefon raqamizni yuboring yoki 
+998991234567, 998991234567, 991234567
ko'rinishlarini birida yozing!"""

def create_student_infos(datas):
    res = "<blockquote>Yangi o'quvchi</blockquote>\n\n"
    res += f"F.I.O.: {datas['student_fullname']}\n"
    res += f"Guruh: {datas['student_group_name']}\n"
    res += f"Fan: {datas['student_subject_name']}\n"
    res += f"Telefon: {datas['student_phone']}\n"
    
    if datas['student_username']:
        res += f"Username: @{datas['student_username']}\n"

    return res



#### TEACHER
TEACHER_WELCOME = """Assalomu alaykum, hurmatli ustoz !"""
TEACHER = """O'qituvchi"""
TEACHER_SELECT = """O'qituvchi sifatida ro'yxatdan o'tish"""
TEACHER_FULLNAME = """Ism-familiyangizni kiriting: """
TEACHER_GROUPS = """Guruhlarim"""
TEACHER_NO_GROUPS = """Sizda mavjud guruhlar yo'q"""
TEACHER_NO_FILES = """Sizda test fayllari yo'q"""
TEACHER_ADD_NEW_GROUP = """Yangi guruh qo'shish"""
TEACHER_SUBJECTS = """Fanlarim"""
TEACHER_SUBJECT_ASK = """Fan tanlang"""
TEACHER_TESTS = """Test qo'shish"""
TEACHER_TEST_START = """Guruh a'zolari orasida test tashkillashtirish"""
TEACHER_TEST_ADD_START = """Yangi testlar uchun fanni tanglang!"""
TEACHER_GROUP_ATTENDANCE = """Davomat"""
PAYMENT = """To'lovlar"""
TEACHER_GROUP_TESTS = """Test uyushtirish"""
STATISTICS = """Statistika"""

TEACHER_NOTE = \
"""Xabarga e'tibor berishingiz kerak, chunki bu o'quvchi
bazaga saqlangan!"""

TEACHER_PHONE_ASK = \
"""Telefon raqamizni yuboring yoki 
+998991234567, 998991234567, 991234567
ko'rinishlarini birida yozing!"""
TEACHER_SEND_DATAS = """Ma'lumotlarni adminga yuborish"""

def create_teacher_infos(datas):
    res = "<blockquote>Yangi o'qituvchi</blockquote>\n\n"
    res += f"F.I.O.: {datas['teacher_fullname']}\n"
    res += f"Fan: {datas['teacher_subject']}\n"
    res += f"Telefon: {datas['teacher_phone']}\n"
    
    if datas['teacher_username']:
        res += f"Username: @{datas['teacher_username']}\n"

    return res 


# TESTS
TEST_SELECT = """Testlar"""
TEST_START = """Boshlash"""
TEST_ACCEPTED_COUNT = """Qabul qilganlar soni: """
TEST_END_REQUEST = """Tugatish"""
TEST_END = """Test yakunlandi"""
TEST_RESULT = """Natija: """
TESTS = """Test ishlash"""
TEST_STARTED_WHO = """Testni ishlashni boshladi: """
TEST_DONT_STARTED_WHO = """Testni rad etdi: """
TEST_RESULT_SENDED = """Test natijalari o'qituvchiga yuborildi!"""
TEST_TIME_NOTIFY = """Ushbu testni 1 kun muddat ichida topshirishingiz mumkin!"""
TEST_TIME_ENDED = """Ushbu testni topshirish muddati o'tib ketgan!"""
TESTS_NOT_FOUND = """Hozircha testlar qo'shilmagan!"""
TEST_COUNT = """Savollar sonini belgilang: """
TEST_COUNT_ERROR = """Savollar soni juda kam yoki ko'p !"""
TESTS_READING = """Savollar tayyorlanmoqda..."""
TESTS_READY = """Savollar tayyor!"""
TESTS_READY_ERROR = """So'ralgan savollar soni mavjud savollardan ko'p"""
TEST_INCORRECT = """Javobingiz xato!"""
TEST_CORRECT = """Javobingiz to'g'ri!"""
TEST_NOT_SELECTED = """Javob belgilanmagan!"""
TEST_FILE_SELECT = """Test faylingizni tanlang:"""

TESTS_ALREADY_ENDED = \
"""Test uchun ajratilgan vaqt tugadi!!!
<Tugatish> ni bosing!"""


def create_test_result(datas):
    res = f"<blockquote>Testni yakunladi!</blockquote>\n\n"
    res += f"     O'quvchi: {datas['student_fullname']}\n"
    res += f"     Fan: {datas['test_subjectname']}\n"
    res += f"     Test: {datas['test_name']}\n"
    res += f"     Natija: {datas['test_result']}\n"
    res += f"     Yuborilgan: {datas['test_sended_time']}\n"
    res += f"     Tugatilgan: {datas['test_ended_time']}\n"
    res += "#natija"
    
    return res
    

async def create_test_info(datas):
    res = f"<blockquote>Testda qatnashish</blockquote>\n\n"
    res += f"   O'qituvchi: {datas['current_teacher']['teacher_fullname']}\n"
    res += f"   Fan: {datas['teacher_current_test_subject']['subjectname']}\n"
    res += f"   Guruh: {datas['teacher_current_group']['group_name']}\n"
    res += f"   Savollar soni: {datas['teacher_current_test_count']}\n"
    
    return res


def test_time_notify(count):
    res = f"""Har bir savol uchun standart 2 daqiqadan jami 
    {2 * count} daqiqa vaqtingiz bor!"""
    
    return res


# SUBJECTS
SUBJECTS_NOT_FOUND = """Hozircha fanlar qo'shilmagan!"""
SUBJECTS_SELECT = """Fanni tanlang:"""


# OTHERS
BACK = """Orqaga"""
CONFIRM = """Tasdiqlash"""
CONFIRMED = """✅Tasdiqlangan natijalar:"""
NOT_CONFIRMED = """Tasdiqlanmagan natijalar:"""
CANCEL = """Bekor qilish"""
PAID = """To'landi ✅"""
UNPAID = """To'lanmagan ❌"""
RETRY_SELECTING = """Tanlang:"""
ACCEPTED = """Qabul qilindi!"""
SEND_CONTACT = """Raqamni yuborish"""

SENDED = \
"""MA'LUMOTLAR YUBORILDI!
Iltimos natijani kuting, ungacha bot sizga javob bermaydi!"""

WRONG_CONTACT = """Raqam noto'g'ri formatda yuborildi!"""
TELEGRAM_NAME_SUFFIX = """\n[Telegram ism]"""
YES_TEXT = """Qabul qilish"""
NO_TEXT = """Rad etish"""

USER_NOT_ACCEPTED = """Siz qabul qilinmadingiz! Qayta foydalanish uchun  /start buyrug'ini yuboring!"""
USER_ACCEPTED = """Siz qabul qilindingiz!, /start buyrug'ini yuboring!"""

SOMETHING = """yana nimadir"""

NEXT_PAGE = """Keyingi"""
PREV_PAGE = """Oldingi"""
RANDOM = """Aralash"""

NO_STATS = """📊 Sizda statistik ma'lumotlar mavjud emas!"""
NO_GROUPS = """Bu fan uchun guruhlar hali yaratilmagan!"""
GROUPS = """Guruhlar"""
REASON = """Rad etish sababi: """
SENDED = """Xabar yuborildi!"""
RETURNED = """Qaytildi!"""
AVAILABLE_TESTS_COUNT = """Mavjud testlar soni: """
AVAILABLE_TESTS_COUNT_ERROR = """Testlar sonini oshib ketdi!"""
SENDED_STUDENTS_COUNT = """Qatnashish uchun so'rov yuborilganlar soni: """
ATTENDANCE_SAVED = """Davomat saqlandi!"""
PAYMENTS_SAVED = """To'lovlar saqlandi!"""
PAYMENTS_SENDED = """To'laganlik haqidagi ma'lumotlar jo'natildi!"""
SPLITTER = """🎃🎃🎃"""

DAYS_OF_WEEK = ['Du', 'Se', 'Chor', 'Pay', 'Ju', 'Shan', 'Yak']
DAYS_OF_WEEK_ERROR = """Hafta kunlari tanlanmadi!"""

ASK_NEW_GROUP_NAME = """Yangi guruh uchun nom kiriting: """
ASK_NEW_GROUP_SUBJECT = """Yangi guruh uchun fanni tanlang: """
ASK_NEW_GROUP_DAYS = """Yangi guruh uchun dars bo'ladigan hafta kunlarini belgilang: """
ASK_NEW_GROUP_TIMES = """Yangi guruh uchun dars boshlanadigan soatlarni belgilang: """
NEW_GROUP_TIMES_ERROR = """Dars vaqti juda erta yoki juda kech bo'lmaydiku!"""
NEW_GROUP_CREATED = """Yangi guruh yaratildi!"""

ASK_FILE = """Savollarning .xlsx faylini yuboring (max. 20MB)"""
FILE_TYPES = ['xlsx', 'xlsm', 'xlsb', 'xltx', 'xltm', 'xlam', 'csv']
FILE_TYPE_ERROR = """Fayl turida xatolik !"""
FILE_ACCEPTING = """Test yaratish jarayoni natijasi haqida tezda xabar beriladi!"""
FILE_ACCEPT = """Testlar yaratildi!"""
FILE_UNACCEPT = """Faylni tekshirib, qayta urinib ko'ring!"""