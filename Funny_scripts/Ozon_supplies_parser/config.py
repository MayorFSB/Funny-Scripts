import webbrowser

available_ozon_card = False
available_notifications = False

open_in_browser = True
chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
