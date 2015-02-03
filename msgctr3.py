# Embedded file name: msgctr.py
# File: B (Python 2.7)
"""
 Name: Mav's Clan Message Centre 3.06
"""
# Imports
import BigWorld, os, GUI, urllib, ResMgr, time
from gui import SystemMessages
from debug_utils import LOG_ERROR,LOG_NOTE,LOG_CURRENT_EXCEPTION
from gui.shared import events
from Account import Account
from threading import Thread

LOG_NOTE("Initializing Mav's Clan Message Center 3.06")
BigWorld.flushPythonLog()

waitForConnection = Account.onBecomePlayer

class MessageCenter(Thread):
#######################################################
# Set Initial Values
  def __init__(self):
    self.player = ''
    self.sys_msg = ''
    self.initialMSG = True
    self.type = SystemMessages.SM_TYPE.GameGreeting
    self.msgTime = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))
    self.PrimaryToggle = 'ON'
    self.SecondaryTToggle = 'ON'
    self.SecondaryCWToggle = 'ON'
    self.hheight = '34'
    self.hwidth = '220'
    self.dheight = '10'
    self.dwidth = '220'
    self.msgMOTDEnabled = 'yes'
    self.msgMOTDmsg = 'Unable to retrieve primary messages'
    self.MOTDcolor = 'FFB300'
    self.AuthorEnabled = 'no'
    self.msgMEnabled = 'no'
    self.CheckTimer = 5
    self.msgEnabledTourney = 'no'
    self.secondaryTourney = 'yes'
    self.msgEnabledCW = 'no'
    self.secondaryCW = 'yes'
    self.msgSTourneymsg = ''
    self.msgEnabledSTourney = 'no'
    self.combineTourney = 'yes'
    self.tourneyColor = 'FFCC00'
    self.msgEnabledSCW = 'no'
    self.msgSCWmsg = ''
    self.combineCW = 'yes'
    self.cwColor = 'FFCC00'
    self.PlaceHolder = 'Nothing to report at this time'
    self.UpdateCFG = 'no'
    self.modUpdated = 'NO'
    self.UpdateMODUrl = ''
#    self.MsgCTRupdated = 'Mod has updated!'
    # Create folder if necessary
    wotVersionCheck = ResMgr.openSection('../version.xml')
    try:
      self.wotVersion = wotVersionCheck.readString('version')
      self.wotVersion = self.wotVersion.split('#', 1)[0]
      self.wotVersion = self.wotVersion.split('v.', 1)[-1]
      self.wotVersion = self.wotVersion.strip()
      self.scriptFolder = 'res_mods/' + self.wotVersion + '/scripts/client/mods/'
      self.modFolder = self.scriptFolder + 'msg-ctr/'
      self.msgCTRxml = self.scriptFolder + 'msg-ctr.xml'
      self.pMsgXML = self.modFolder + 'primary.xml'
      self.stMsgXML = self.modFolder + 'secondary-tourney.xml'
      self.scwMsgXML = self.modFolder + 'secondary-clan-wars.xml'
      self.uMODsave = self.scriptFolder + 'msgctr.pyc'
      self.hpath = self.modFolder + 'msg-ctr-header.png'
      self.dpath = self.modFolder + 'msg-ctr-divider.png'
      #LOG_ERROR('%s' % (self.modFolder))
    except:
      pass
    if not os.path.exists(self.modFolder):
      LOG_NOTE('Creating directory to store messages')
      os.makedirs(self.modFolder)
    # Parse config
    self.msgCFGmsg = ResMgr.openSection('scripts/client/mods/msg-ctr.xml')
    if self.msgCFGmsg is None:
      LOG_ERROR('Unable to open msg-ctr.xml, attempting to download default configuration')
      try:
        # LOG_ERROR('%s' % (self.msgCTRxml))
        BigWorld.flushPythonLog()
        urllib.urlretrieve("http://pastebin.com/raw.php?i=HT5NU2D5", self.msgCTRxml)
      except:
        LOG_ERROR('Unable to download replacement msg-ctr.xml')
      self.msgCFGmsg = ResMgr.openSection('scripts/client/mods/msg-ctr.xml')
      self.rtrURL = self.msgCFGmsg.readString('Primary_Message_Address').strip()
      self.rtrTournURL = self.msgCFGmsg.readString('Secondary_Tourney_Address').strip()
      self.rtrCWarsURL = self.msgCFGmsg.readString('Secondary_CW_Address').strip()
      self.imgHUrl = self.msgCFGmsg.readString('Header_Graphic').strip()
      self.hheight = self.msgCFGmsg.readString('Header_Height').strip()
      self.hwidth = self.msgCFGmsg.readString('Header_Width').strip()
      self.imgDUrl = self.msgCFGmsg.readString('Divider_Graphic').strip()
      self.dheight = self.msgCFGmsg.readString('Divider_Height').strip()
      self.dwidth = self.msgCFGmsg.readString('Divider_Width').strip()
      LOG_NOTE('Downloaded default configuration file')
    else:
      self.rtrURL = self.msgCFGmsg.readString('Primary_Message_Address').strip()
      self.rtrTournURL = self.msgCFGmsg.readString('Secondary_Tourney_Address').strip()
      self.rtrCWarsURL = self.msgCFGmsg.readString('Secondary_CW_Address').strip()
      self.imgHUrl = self.msgCFGmsg.readString('Header_Graphic').strip()
      self.hheight = self.msgCFGmsg.readString('Header_Height').strip()
      self.hwidth = self.msgCFGmsg.readString('Header_Width').strip()
      self.imgDUrl = self.msgCFGmsg.readString('Divider_Graphic').strip()
      self.dheight = self.msgCFGmsg.readString('Divider_Height').strip()
      self.dwidth = self.msgCFGmsg.readString('Divider_Width').strip()
      LOG_NOTE('----------------------------------------------------------------------------------------------\nOpened msg-ctr.xml: \nPrimary Message URL: %s \nSecondary Tournament URL: %s \nSecondary CW URL: %s \nHeader Graphic: %s \nDivider Graphic: %s' % (self.rtrURL, self.rtrTournURL, self.rtrCWarsURL, self.imgHUrl, self.imgDUrl))
      LOG_NOTE('----------------------------------------------------------------------------------------------')
    self.retrievePrimary()
    self.retrieveSecondaryT()
    self.retrieveSecondaryCW()
    LOG_NOTE('Initialized')
#    LOG_NOTE('self.LoggedIn %s \nplayer %s \nsys_msg %s \nself.msgTime %s' % (self.LoggedIn, self.player, self.sys_msg, self.msgTime))
    BigWorld.flushPythonLog()

#####################################################################
#####################################################################
# Retrieve primary.xml
  def retrievePrimary(self):
    LOG_NOTE('Attempting to retrieve primary messages')
    try:
      urllib.urlretrieve('%s' % (self.rtrURL), self.pMsgXML)
    except:
      self.PrimaryToggle = 'OFF'
      LOG_ERROR('Unable to retrieve primary message from %s' % (self.rtrURL))
    LOG_NOTE('Completed')

#####################################################################
# Parse primary message file
    LOG_NOTE('Attempting to parse primary messages')
    #try:
    #  if self.primaryMsgXML is not None:
    #    ResMgr.purge('scripts/client/mods/msg-ctr/primary.xml')
    #    LOG_NOTE('Re-checking primary.xml')
    #except:
    #  LOG_NOTE('')
    self.primaryMsgXML = ResMgr.openSection('scripts/client/mods/msg-ctr/primary.xml')
    try:
      if self.primaryMsgXML is not None:
        self.Author = self.primaryMsgXML.readString('Author')
        self.authorColor = self.primaryMsgXML.readString('Author_Color').strip()
        self.AuthorEnabled = self.primaryMsgXML.readString('Show_Author').strip().lower()
        self.CheckTimer = int(self.primaryMsgXML.readString('Check_Message_Time').strip())
  # MOTD
        self.msgMOTDEnabled = self.primaryMsgXML.readString('Show_MOTD_Message').strip().lower()
        self.msgMOTDmsg = self.primaryMsgXML.readString('MOTDmsg')
        self.MOTDcolor = self.primaryMsgXML.readString('MOTD_Color').strip()
  # Meetings
        self.msgMEnabled = self.primaryMsgXML.readString('Show_Meeting_Message').strip().lower()
        self.msgMeetingmsg = self.primaryMsgXML.readString('Clan_Meeting')
        self.MeetingColor = self.primaryMsgXML.readString('Meeting_Color').strip()
  # Tournaments
        self.msgEnabledTourney = self.primaryMsgXML.readString('Show_Tourney_Message').strip().lower()
        self.msgTourney = self.primaryMsgXML.readString('Tournament_Battles_Message')
        self.tourneyColor= self.primaryMsgXML.readString('Tournament_Color').strip()
        self.secondaryTourney = self.primaryMsgXML.readString('Enable_Secondary_Tourney').strip().lower()
        self.combineTourney = self.primaryMsgXML.readString('Show_Both_TMessages').strip().lower()
  # Clan Wars
        self.msgEnabledCW = self.primaryMsgXML.readString('Show_Clanwars_Message').strip().lower()
        self.msgCWmsg = self.primaryMsgXML.readString('Clan_Wars_Message')
        self.cwColor = self.primaryMsgXML.readString('CW_Color').strip()
        self.secondaryCW = self.primaryMsgXML.readString('Show_Secondary_CW').strip().lower()
        self.combineCW = self.primaryMsgXML.readString('Show_Both_CWMessages').strip().lower()
  # msg-ctr.xml status
        self.UpdateCFG = self.primaryMsgXML.readString('Update_Mod_Config')
        self.UpdateCFGurl = self.primaryMsgXML.readString('Config_Update_Address')
  # is update tag present?
        try:
          self.UpdateMODUrl = self.primaryMsgXML.readString('Update_Mod_URL')
          if 'http' in self.UpdateMODUrl:
            try:
              urllib.urlretrieve('%s' % (self.UpdateMODUrl), self.uMODsave)
            except:
              LOG_CURRENT_EXCEPTION()
            self.modUpdated = 'YES'
            LOG_NOTE('Updated Mod!')
        except:
          pass
        LOG_NOTE('----------------------------------------------------------------------------------------------\nSuccessfully read primary.xml, values are: \nAuthor: %s \nShow Author: %s \nCheck Time: %s \nMOTD: %s \nMOTD Enabled: %s \nMeeting Message: %s \nMeeting Message Enabled: %s \n- - -\nTourney Message: %s \nTourney Message Enabled: %s \nSecondary Tourney Message Status: %s \nCombine Both Tourney Messages: %s \n- - -\nClan Wars Message: %s \nClan Wars Message Enabled: %s \nSecondary Clan Wars Message Status: %s \nCombine Both Clan Wars Messages: %s \n- - -\nShould msg-ctr.xml be updated: %s \nLocation to get updated msg-ctr.xml: %s' % (self.Author, self.AuthorEnabled, self.CheckTimer, self.msgMOTDmsg, self.msgMOTDEnabled, self.msgMeetingmsg, self.msgMEnabled, self.msgTourney, self.msgEnabledTourney, self.secondaryTourney, self.combineTourney, self.msgCWmsg, self.msgEnabledCW, self.secondaryCW, self.combineCW, self.UpdateCFG, self.UpdateCFGurl))
        LOG_NOTE('----------------------------------------------------------------------------------------------\nCOLOR SETTINGS\nAuthor color: %s \nMOTDcolor: %s \nTourney_Color: %s \nCW Color: %s' % (self.authorColor, self.MOTDcolor, self.tourneyColor, self.cwColor))
      else:
        LOG_ERROR('Unable to read primary.xml')
      #LOG_NOTE('Author color: %s \nMOTDcolor: %s \nTourney_Color: %s \nCW Color: %s' % (self.authorColor, self.MOTDcolor, self.tourneyColor, self.cwColor))
    except:
      LOG_CURRENT_EXCEPTION()
    #LOG_NOTE('Completed parsing primary messages')
    LOG_NOTE('----------------------------------------------------------------------------------------------')
    if self.UpdateCFG == 'yes':
      self.UpdateMSGConfig()
############# make sure doesn't create circular loop
    else:
      self.checkMsgGraphics()

#####################################################################
#####################################################################
# Should msg-ctr.xml be updated?
  def UpdateMSGConfig(self):
    if self.UpdateCFG == 'yes' and 'http' in self.UpdateCFGurl:
      LOG_NOTE('Attempting to download updated configuration file msg-ctr.xml')
      try:
        urllib.urlretrieve('%s' % (self.UpdateCFGurl), self.msgCTRxml)
      except:
        LOG_ERROR('Unable to download updated msg-ctr.xml from %s' % (self.UpdateCFGurl))
        self.UpdateCFG = 'no'
      if self.UpdateCFG == 'yes':
        ResMgr.purge('scripts/client/mods/msg-ctr.xml')
        self.msgUCFGmsg = ResMgr.openSection('scripts/client/mods/msg-ctr.xml')
        self.rtrURL = msgUCFGmsg.readString('Primary_Message_Address')
        self.rtrTournURL = msgUCFGmsg.readString('Secondary_Tourney_Address')
        self.rtrCWarsURL = msgUCFGmsg.readString('Secondary_CW_Address')
        self.imgHUrl = msgUCFGmsg.readString('Header_Graphic')
        self.imgDUrl = msgUCFGmsg.readString('Divider_Graphic')
      LOG_NOTE('Downloaded updated msg-ctr.xml from %s' % (self.UpdateCFGurl))
    self.checkMsgGraphics()

#####################################################################
#####################################################################
# Determine if using local or remote header graphic

  def checkMsgGraphics(self):
    self.MsgHeader = '<img src="img://scripts/client/mods/msg-ctr/msg-ctr-header.png" height="' + self.hheight + '" width="' + self.hwidth + '">'
    if self.imgHUrl is not None and "http" in self.imgHUrl:
      LOG_NOTE('Downloading header graphic from %s' % (self.imgHUrl))
      try: 
        urllib.urlretrieve('%s' % (self.imgHUrl), self.hpath)
      except:
        LOG_NOTE('Failed to download header graphic from %s reverting to local copy' % (self.imgHUrl))
      LOG_NOTE('Loaded header graphic from %s' % (self.imgHUrl))
    else:
      self.MsgHeader = '<img src="' + self.imgHUrl + '" height="' + self.hheight + '" width="' + self.hwidth + '">'
      LOG_NOTE('Using local header %s' % (self.MsgHeader))

#####################################################################
# Determine if using local or remote divider graphic
    self.MsgDivider = '<img src="img://scripts/client/mods/msg-ctr/msg-ctr-divider.png" height="' + self.dheight + '" width="' + self.dwidth + '">'
    if self.imgDUrl is not None and "http" in self.imgDUrl:
      LOG_NOTE('downloading divider graphic from %s' % (self.imgDUrl))
      try: 
        urllib.urlretrieve('%s' % (self.imgDUrl), self.dpath)
      except:
        LOG_NOTE('Failed to download divider graphic from %s reverting to local copy' % (self.imgDUrl))
      LOG_NOTE('Loaded divider graphic from %s' % (self.imgDUrl))
    else:
      self.MsgDivider = '<img src="' + self.imgDUrl + '" height="' + self.dheight + '" width="' + self.dwidth + '">'
      LOG_NOTE('Using local divider %s' % (self.MsgDivider))
    LOG_NOTE('----------------------------------------------------------------------------------------------')

#####################################################################
#####################################################################
# Read secondary tournament messages
  def retrieveSecondaryT(self):
    if self.secondaryTourney == 'yes':
      LOG_NOTE('Downloading secondary tournament details')
      try:
        urllib.urlretrieve('%s' % (self.rtrTournURL), self.stMsgXML)
      except:
        self.SecondaryTToggle = 'OFF'
        LOG_ERROR('Unable to download secondary tournament details from %s' % (self.rtrTournURL))

#####################################################################
# Parse secondary tournament message file
      self.tourneyMsgXML = ResMgr.openSection('scripts/client/mods/msg-ctr/secondary-tourney.xml')
      if self.tourneyMsgXML is not None:
        try:
          self.msgEnabledSTourney = self.tourneyMsgXML.readString('Show_Tourney_Message').strip().lower()
          self.msgSTourneymsg = self.tourneyMsgXML.readString('Tournament_Battles_Message')
          LOG_NOTE('Parsed secondary-tourney.xml, values are: \nSecondary Tourney Details: %s \nEnabled: %s' % (self.msgSTourneymsg, self.msgEnabledSTourney))
          BigWorld.flushPythonLog()
        except:
          LOG_CURRENT_EXCEPTION()
          self.msgEnabledSTourney = 'no'
      else:
        LOG_ERROR('Unable to parse secondary-tourney.xml')
      #LOG_NOTE('Success!')

#####################################################################
# Combine primary and secondary tournament messages if required
      if self.combineTourney == 'yes':
        if self.msgEnabledTourney == 'yes' and self.msgEnabledSTourney == 'yes':
#          LOG_NOTE('Primary Tourney Enabled: %s and Secondary Tourney Enabled: %s' % (self.msgEnabledTourney, self.msgEnabledSTourney))
          LOG_NOTE('Combining primary and secondary tournament messages')
          self.msgTourney = self.msgTourney + '\n' + self.MsgDivider + '\n' + self.msgSTourneymsg
        elif self.msgEnabledTourney == 'no' and self.msgEnabledSTourney == 'yes':
          LOG_NOTE('Primary tournament message is disabled, using secondary message instead')
          self.msgTourney = self.msgSTourneymsg
        else:
          LOG_NOTE("Secondary tournament messages are disabled")
      elif self.combineTourney == 'no':
        if self.msgEnabledTourney == 'yes' and self.msgEnabledSTourney =='yes':
          LOG_NOTE('Tournament message combining is disabled, replacing primary message with secondary')
          self.msgTourney = self.msgSTourneymsg
    else:
      self.msgEnabledSTourney = 'no'
      LOG_NOTE('Primary and secondary tournament messages are disabled')
    LOG_NOTE('----------------------------------------------------------------------------------------------')

#####################################################################
#####################################################################
# Read secondary clan wars messages
  def retrieveSecondaryCW(self):
    if self.secondaryCW == 'yes':
      LOG_NOTE('Downloading secondary clan wars details')
      try:
        urllib.urlretrieve('%s' % (self.rtrCWarsURL), self.scwMsgXML)
      except:
        self.SecondaryCWToggle = 'OFF'
        LOG_ERROR('Unable to download secondary clan wars details from %s' % (self.rtrCWarsURL))

#####################################################################
# Parse secondary clan wars message file
      self.CWMsgXML = ResMgr.openSection('scripts/client/mods/msg-ctr/secondary-clan-wars.xml')
      if self.CWMsgXML is not None:
        try:
          self.msgEnabledSCW = self.CWMsgXML.readString('Show_Clanwars_Message').strip().lower()
          self.msgSCWmsg = self.CWMsgXML.readString('Clan_Wars_Message')
          LOG_NOTE('Parsed secondary-clan-wars.xml, values are: \nSecondary Clanwars Details: %s \nEnabled: %s' % (self.msgSCWmsg, self.msgEnabledSCW))
        except:
          LOG_CURRENT_EXCEPTION()
          self.msgEnabledSCW = 'no'
      else:
        LOG_ERROR('Unable to parse secondary-clan-wars.xml')
      #LOG_NOTE('Success!')

#####################################################################
# Combine primary and secondary CW messages if required
      if self.combineCW == 'yes':
        if self.msgEnabledCW == 'yes' and self.msgEnabledSCW == 'yes':
          LOG_NOTE('Combining primary and secondary clanwars messages')
          self.msgCWmsg = self.msgCWmsg + '\n' + self.MsgDivider + '\n' + self.msgSCWmsg
        elif self.msgEnabledCW == 'no' and self.msgEnabledSCW == 'yes':
          LOG_NOTE('Primary clanwars message is disabled, using secondary message instead')
          self.msgCWmsg = self.msgSCWmsg
        else:
          LOG_NOTE("Secondary clanwars message disabled")
      elif self.combineCW == 'no':
        LOG_NOTE('Clanwars message combining is disabled')
        if self.msgEnabledCW == 'yes' and self.msgEnabledSCW =='yes':
          LOG_NOTE('Replacing primary message with secondary')
          self.msgCWmsg = self.msgSCWmsg
    else:
      self.msgEnabledSCW = 'no'
      LOG_NOTE('Primary and secondary clan wars messages are disabled')
    LOG_NOTE('----------------------------------------------------------------------------------------------')




#######################################################
# Logging in
  def PlayerLoggingIn(self):
    LOG_NOTE('Player logging in')
    BigWorld.flushPythonLog()
    msgCTRLoad.calculate()
    waitForConnection(self)
  Account.onBecomePlayer = PlayerLoggingIn



#######################################################
# Calculate time since last check
  def calculate(self):
    self.nowTime = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))

    if self.nowTime < self.msgTime:
      self.nowTime = self.nowTime + 1440
      self.difTime = self.nowTime - self.msgTime
      LOG_NOTE('\nself.msgTime is %s \nself.nowTime: %s \nself.difTime: %s' % (self.msgTime, self.nowTime, self.difTime))
      BigWorld.flushPythonLog()
    else:
      self.difTime = self.nowTime - self.msgTime
      LOG_NOTE('\nLast message time was %s \nCurrent time is: %s \nDifference of: %s' % (self.msgTime, self.nowTime, self.difTime))
      BigWorld.flushPythonLog()

    if self.initialMSG == True:
      self.msgTime = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))
      LOG_NOTE('sending initial message')
      BigWorld.flushPythonLog()
      self.initialMSG = False
      self.messaging()
    elif self.difTime >= self.CheckTimer:
      LOG_NOTE('Difference is greater than %s, re-checking messages' % (self.CheckTimer))
      BigWorld.flushPythonLog()
      self.msgTime = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))
      self.erase()
      self.retrievePrimary()
      self.retrieveSecondaryT()
      self.retrieveSecondaryCW()
      self.messaging()
    else:
      LOG_NOTE('Difference is less than %s' % (self.CheckTimer))
      BigWorld.flushPythonLog()

#######################################################
# Purge Existing Messages For Re-Check
  def erase(self):
    ResMgr.purge('scripts/client/mods/msg-ctr/primary.xml')
    ResMgr.purge('scripts/client/mods/msg-ctr/secondary-tourney.xml')
    ResMgr.purge('scripts/client/mods/msg-ctr/secondary-clan-wars.xml')
    self.sys_msg = ''
    LOG_NOTE('Purged primary.xml, secondary-tourney.xml, and secondary-clan-wars.xml')
    BigWorld.flushPythonLog()

#######################################################
# Send Message
  def msg(self):
    try:
      if (len(self.sys_msg) != 0):
        if SystemMessages.g_instance is None:
          BigWorld.callback(4.0, self.msg)
        else:
          SystemMessages.pushMessage(self.sys_msg,self.type)
    except:
      LOG_CURRENT_EXCEPTION()
    return

#######################################################
# Build Message
  def messaging(self):
    if self.PrimaryToggle == 'OFF':
      self.type = SystemMessages.SM_TYPE.Warning
      self.sys_msg = self.sys_msg + self.MsgHeader + '\n' + self.MsgDivider + '<b>Unable to check for notifications</b>'
#######################################################
# If all checks were successful, present user with messages
    if self.PrimaryToggle == 'ON':
      LOG_NOTE('Telling user messages')
      self.type = SystemMessages.SM_TYPE.GameGreeting
      self.sys_msg = self.sys_msg + self.MsgHeader + '\n' + self.MsgDivider
      if self.msgMOTDEnabled == 'yes':
        self.sys_msg = self.sys_msg + '\n<font color="#' + self.MOTDcolor + '"><b>' + self.msgMOTDmsg + '</b></font>'
      if self.AuthorEnabled == 'yes' and self.msgMOTDEnabled == 'yes':
        self.sys_msg = self.sys_msg + ' -- ' + '<font color="#' + self.authorColor + '">' + self.Author + '</font>\n' + self.MsgDivider
      elif self.msgMOTDEnabled == 'yes' and self.AuthorEnabled != 'yes':
        self.sys_msg = self.sys_msg + '\n' + self.MsgDivider
      if self.msgMEnabled == 'yes':
        self.sys_msg = self.sys_msg + '\n<font color="#' + self.MeetingColor + '">' + self.msgMeetingmsg + '</font>\n' + self.MsgDivider
      if self.msgEnabledTourney == 'yes' or self.msgEnabledSTourney == 'yes':
        self.sys_msg = self.sys_msg + '\n<font color="#' + self.tourneyColor + '">' + self.msgTourney + '</font>\n' + self.MsgDivider
      if self.msgEnabledCW == 'yes' or self.msgEnabledSCW == 'yes':
        self.sys_msg = self.sys_msg + '\n<font color="#' + self.cwColor + '">' + self.msgCWmsg + '</font>\n' + self.MsgDivider
      if self.msgMOTDEnabled != 'yes' and self.msgMEnabled != 'yes' and self.msgEnabledTourney != 'yes' and self.msgEnabledCW != 'yes' and self.msgEnabledSTourney != 'yes' and self.msgEnabledSCW !='yes':
        self.sys_msg = self.sys_msg + '\n<font color="#FFCC00"><b>' + self.PlaceHolder + '</b></font>\n'
      LOG_NOTE('Final output:\n%s' % (self.sys_msg))
      BigWorld.flushPythonLog()
      self.msg()



#######################################################
# Build Message
#  def messaging(self):
#    self.sys_msg = self.sys_msg + '<b>Test message</b>\n'
#    LOG_NOTE('self.sys_msg %s \nplayer is %s' % (self.sys_msg, self.player))
#    BigWorld.flushPythonLog()
#    self.msg()

msgCTRLoad = MessageCenter()
#######################################################
# Logging out/switching servers
#def PlayerLoggingOut(self):
#  LOG_NOTE('User has logged out')
#  BigWorld.flushPythonLog()
#  userLoggingOut(self)
#PlayerAccount.onBecomeNonPlayer = PlayerLoggingOut

BigWorld.flushPythonLog()
