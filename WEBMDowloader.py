import telepot
import urllib.request
import _thread
import ffmpy
import os


def download_file(url, file_name, attempt = 1):
    try:
        print(file_name, 'downloading...')
        urllib.request.urlretrieve(url, directory + file_name)
        return 0
    except:
        if attempt > 3:
            print('Download error, url:', url)
            return -1
        else:
            print('Try to download file again, attempt', attempt)
            return download_file(url, file_name, attempt + 1)


def get_file_name(url):
    return str(url).split('/')[-1]


def get_file_type(file_name):
    return str(file_name).split('/')[-1].split('.')[-1]


def find_url(input_text):
    text_parts = input_text.split(' ')
    for part in text_parts:
        if get_url_validation(part):
            return part
    print('Message do not contains url.')
    return ''


def only_url(input_text):
    if len(input_text.split(' ')) > 1:
        return False
    return True


def get_input_text_without_url(input_text):
    text_parts = input_text.split(' ')
    for i in range(len(text_parts)):
        if get_url_validation(text_parts[i]):
            del text_parts[i]
            return ' '.join(text_parts)


def get_url_validation(url):
    try:
        if str(url).split('/')[0] == 'https:' or str(url).split('/')[0] == 'http:':
            return True
        return False
    except:
        return False
    # Проба с regex
    #reobj = re.compile(r"(https?:\/\/)?([\w\.]+)\.([a-z]{2,6}\.?)(\/[\w\.]*)*\/?$", re.IGNORECASE)
    #afterReUrl = re.findall(reobj, url)
    #for url in afterReUrl: #если есть хотя бы один объект с webm на конце - отправляем True
    #    if str(afterReUrl).split('.')[-1] == 'webm':


def convert(name):
    ff = ffmpy.FFmpeg(
        inputs={directory + name + '.webm': None},
        outputs={name + '.mp4': None}
    )
    ff.run()

def sent_file_to_chat(chat_id, user_name, user_id, input_text):
    global Bot
    print(user_name, 'sent message:', input_text)
    url = find_url(input_text)
    if url == '':
        Bot.sendMessage(user_id, 'Your message do not contains url.')
        return

    file_name = get_file_name(url)
    download_status = download_file(url, file_name)
    if download_status == -1:
        print('Url in message', input_text, 'incorrect.')
        Bot.sendMessage(user_id, 'Url incorrect, try again.')
        return

    print(file_name, 'downloaded, sending...')
    output_file = open(directory + file_name, 'rb')
    message_text = user_name + " sent " + get_file_type(file_name) + ": " + url
    try:
        #convert(file_name.split('.')[0])
        #mp4file = file_name.split('.')[0] + '.mp4'
        Bot.sendDocument(chat_id, (file_name, output_file), message_text)
        #Bot.sendVideo(chat_id, mp4file)
        if not only_url(input_text):
            message_for_commentary_text = user_name + " commentary: " + str(get_input_text_without_url(input_text))
            Bot.sendMessage(chat_id, message_for_commentary_text)
        print(file_name, "sent.")
    except ConnectionError:
        print("Send", file_name, "exception, try again.")
        return
    output_file.close()
    try:
        os.remove(directory + file_name)
        print(file_name, 'deleted.')
    except FileNotFoundError:
        print(file_name, 'did not delete.')
    print('--- work with', file_name, 'ended.')

try:
    token = input()
    Bot = telepot.Bot(token)
    commands = Bot.getUpdates(-10, 10)
except ConnectionError:
    print('Connection error, press any key to exit.')
    input()
    exit()

directory = "C:\\TempFiles\\"
if not os.path.exists(directory):
    os.makedirs(directory)

lastTime = -1
for some_command in commands:
    try:
        lastTime = int(some_command['message']['date'])
    except:
        pass

print('Start to listen...')

while True:
    commands = Bot.getUpdates(-10, 10)
    for some_command in commands:
        try:
            if 'message' in some_command:
                if int(some_command['message']['date']) > lastTime:
                    lastTime = int(some_command['message']['date'])
                    _thread.start_new_thread(sent_file_to_chat, (-199378049,
                                                                str(some_command['message']['from']['username']).title(),
                                                                int(some_command['message']['from']['id']),
                                                                some_command['message']['text']
                                                                )
                                             )
        except:
            print("Something went wrong.")
