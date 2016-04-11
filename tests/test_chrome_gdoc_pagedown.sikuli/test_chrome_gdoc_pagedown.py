import browser
import common
import sys


com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

chrome.clickBar()
chrome.enterLink("https://docs.google.com/document/d/1EpYUniwtLvBbZ4ECgT_vwGUfTHKnqSWi7vgNJQBemFk/edit")

gd.wait_for_loaded()

for i in range(100):
    type(Key.PAGE_DOWN)

wait(5)
chrome.getConsoleInfo("window.performance.timing")
com.dumpToJson(Env.getClipboard(), "timing" + sys.argv[1])
