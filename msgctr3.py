# Embedded file name: msgctr.py
# File: B (Python 2.7)
"""
 Name: Mav's Clan Message Centre 3.01
"""
# Imports
import BigWorld, os, GUI, urllib, ResMgr, time
from gui import SystemMessages
from debug_utils import LOG_ERROR,LOG_NOTE,LOG_CURRENT_EXCEPTION
from gui.shared import events
from Account import Account
from threading import Thread

LOG_NOTE('initializing')
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
    self.PlaceHolder = 'Nothing to report at this time'
#    self.MsgCTRupdated = 'Mod has updated!'
    # Create folder if necessary
    if not os.path.exists('res_mods/0.9.5/scripts/client/mods/msg-ctr'):
      LOG_NOTE('Creating directory to store messages')
      os.makedirs('res_mods/0.9.5/scripts/client/mods/msg-ctr')
    # Parse config
    self.msgCFGmsg = ResMgr.openSection('scripts/client/mods/msg-ctr.xml')
    if self.msgCFGmsg is None:
      LOG_ERROR('Unable to open msg-ctr.xml, attempting to download default configuration')
      try:
        urllib.urlretrieve("http://pastebin.com/raw.php?i=6FhvCbrX", "res_mods/0.9.5/scripts/client/mods/msg-ctr.xml")
      except:
        LOG_ERROR('Unable to download replacement msg-ctr.xml')
      self.msgCFGmsg = ResMgr.openSection('scripts/client/mods/msg-ctr.xml')
      self.rtrURL = self.msgCFGmsg.readString('Primary_Message_Address')
      self.rtrTournURL = self.msgCFGmsg.readString('Secondary_Tourney_Address')
      self.rtrCWarsURL = self.msgCFGmsg.readString('Secondary_CW_Address')
      self.imgHUrl = self.msgCFGmsg.readString('Header_Graphic')
      self.imgDUrl = self.msgCFGmsg.readString('Divider_Graphic')
      LOG_NOTE('Downloaded default configuration file')
    else:
      self.rtrURL = self.msgCFGmsg.readString('Primary_Message_Address')
      self.rtrTournURL = self.msgCFGmsg.readString('Secondary_Tourney_Address')
      self.rtrCWarsURL = self.msgCFGmsg.readString('Secondary_CW_Address')
      self.imgHUrl = self.msgCFGmsg.readString('Header_Graphic')
      self.imgDUrl = self.msgCFGmsg.readString('Divider_Graphic')
      LOG_NOTE('----------------------------------------------------------------------------------------------\nOpened msg-ctr.xml: \nPrimary Message URL: %s \nSecondary Tournament URL: %s \nSecondary CW URL: %s \nHeader Graphic: %s \nDivider Graphic: %s' % (self.rtrURL, self.rtrTournURL, self.rtrCWarsURL, self.imgHUrl, self.imgDUrl))
      LOG_NOTE('----------------------------------------------------------------------------------------------')
    self.retrievePrimary()
    self.retrieveSecondaryT()
    self.retrieveSecondaryCW()
    LOG_NOTE('initialized')
#    LOG_NOTE('self.LoggedIn %s \nplayer %s \nsys_msg %s \nself.msgTime %s' % (self.LoggedIn, self.player, self.sys_msg, self.msgTime))
    BigWorld.flushPythonLog()

#####################################################################
# Retrieve primary.xml
  def retrievePrimary(self):
    LOG_NOTE('Retrieving primary messages')
    try:
      urllib.urlretrieve('%s' % (self.rtrURL), "res_mods/0.9.5/scripts/client/mods/msg-ctr/primary.xml")
    except:
      self.PrimaryToggle = 'OFF'
      LOG_ERROR('Unable to retrieve primary message from %s' % (self.rtrURL))
    LOG_NOTE('Finished retrieving primary messages')

#####################################################################
# Parse primary message file
    LOG_NOTE('Attempting to parse primary messages')
    self.primaryMsgXML = ResMgr.openSection('scripts/client/mods/msg-ctr/primary.xml')
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
      self.msgMeeting = self.primaryMsgXML.readString('Clan_Meeting')
      self.MeetingColor = self.primaryMsgXML.readString('Meeting_Color').strip()
  # Tournaments
      self.msgEnabledTourney = self.primaryMsgXML.readString('Show_Tourney_Message').strip().lower()
      self.msgTourney = self.primaryMsgXML.readString('Tournament_Battles_Message')
      self.Tourney_Color= self.primaryMsgXML.readString('Tournament_Color').strip()
      self.secondaryTourney = self.primaryMsgXML.readString('Enable_Secondary_Tourney').strip().lower()
      self.combineTourney = self.primaryMsgXML.readString('Show_Both_TMessages').strip().lower()
  # Clan Wars
      self.msgEnabledCW = self.primaryMsgXML.readString('Show_Clanwars_Message').strip().lower()
      self.msgCWmsg = self.primaryMsgXML.readString('Clan_Wars_Message')
      self.CWColor = self.primaryMsgXML.readString('CW_Color').strip()
      self.secondaryCW = self.primaryMsgXML.readString('Show_Secondary_CW').strip().lower()
      self.combineCW = self.primaryMsgXML.readString('Show_Both_CWMessages').strip().lower()
  # msg-ctr.xml status
      self.UpdateCFG = self.primaryMsgXML.readString('Update_Mod_Config')
      self.UpdateCFGurl = self.primaryMsgXML.readString('Config_Update_Address')
      LOG_NOTE('----------------------------------------------------------------------------------------------\nSuccessfully read primary.xml, values are: \nAuthor: %s \nShow Author: %s \nCheck Time: %s \nMOTD: %s \nMOTD Enabled: %s \nMeeting Message: %s \nMeeting Message Enabled: %s \n- - -\nTourney Message: %s \nTourney Message Enabled: %s \nSecondary Tourney Message Status: %s \nCombine Both Tourney Messages: %s \n- - -\nClan Wars Message: %s \nClan Wars Message Enabled: %s \nSecondary Clan Wars Message Status: %s \nCombine Both Clan Wars Messages: %s \n- - -\nShould msg-ctr.xml be updated: %s \nLocation to get updated msg-ctr.xml: %s' % (self.Author, self.AuthorEnabled, self.CheckTimer, self.msgMOTDmsg, self.msgMOTDEnabled, self.msgMeeting, self.msgMEnabled, self.msgTourney, self.msgEnabledTourney, self.secondaryTourney, self.combineTourney, self.msgCWmsg, self.msgEnabledCW, self.secondaryCW, self.combineCW, self.UpdateCFG, self.UpdateCFGurl))
      LOG_NOTE('----------------------------------------------------------------------------------------------\nCOLOR SETTINGS\nAuthor color: %s \nMOTDcolor: %s \nTourney_Color: %s \nCW Color: %s' % (self.authorColor, self.MOTDcolor, self.Tourney_Color, self.CWColor))
    else:
      LOG_ERROR('Unable to read primary.xml')
      #LOG_NOTE('Author color: %s \nMOTDcolor: %s \nTourney_Color: %s \nCW Color: %s' % (self.authorColor, self.MOTDcolor, self.Tourney_Color, self.CWColor))
    LOG_NOTE('Completed parsing primary messages')
    LOG_NOTE('----------------------------------------------------------------------------------------------')
    if self.UpdateCFG == 'yes':
      self.UpdateMSGConfig()
############# make sure doesn't create circular loop
    else:
      self.checkMsgGraphics()

#####################################################################
# Should msg-ctr.xml be updated?
  def UpdateMSGConfig(self):
    if self.UpdateCFG == 'yes' and 'http' in self.UpdateCFGurl:
      LOG_NOTE('Attempting to download updated configuration file msg-ctr.xml')
      try:
        urllib.urlretrieve('%s' % (self.UpdateCFGurl), "res_mods/0.9.5/scripts/client/mods/msg-ctr.xml")
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
# Determine if using local or remote header graphic

  def checkMsgGraphics(self):
    self.MsgHeader = '<img src="img://scripts/client/mods/msg-ctr/msg-ctr-header.png" height="34" width="220">'
    if self.imgHUrl is not None and "http" in self.imgHUrl:
      LOG_NOTE('Downloading header graphic from %s' % (self.imgHUrl))
      try: 
        urllib.urlretrieve('%s' % (self.imgHUrl), "res_mods/0.9.5/scripts/client/mods/msg-ctr/msg-ctr-header.png")
      except:
        LOG_NOTE('Failed to download header graphic from %s reverting to local copy' % (self.imgHUrl))
      LOG_NOTE('Loaded header graphic from %s' % (self.imgHUrl))
    else:
      self.MsgHeader = '<img src="' + self.imgHUrl + '" height="34" width="220">'
      LOG_NOTE('Using local header %s' % (self.MsgHeader))

#####################################################################
# Determine if using local or remote divider graphic
    self.MsgDivider = '<img src="img://scripts/client/mods/msg-ctr/msg-ctr-divider.png" height="10" width="220">'
    if self.imgDUrl is not None and "http" in self.imgDUrl:
      LOG_NOTE('downloading divider graphic from %s' % (self.imgDUrl))
      try: 
        urllib.urlretrieve('%s' % (self.imgDUrl), "res_mods/0.9.5/scripts/client/mods/msg-ctr/msg-ctr-divider.png")
      except:
        LOG_NOTE('Failed to download divider graphic from %s reverting to local copy' % (self.imgDUrl))
      LOG_NOTE('Loaded divider graphic from %s' % (self.imgDUrl))
      LOG_NOTE('----------------------------------------------------------------------------------------------')
    else:
      self.MsgDivider = '<img src="' + self.imgDUrl + '" height="10" width="220">'
      LOG_NOTE('Using local divider %s' % (self.imgDUrl))

#####################################################################
#####################################################################
# Read secondary tournament messages
  def retrieveSecondaryT(self):
    if self.secondaryTourney == 'yes':
      LOG_NOTE('Downloading secondary tournament details')
      try:
        urllib.urlretrieve('%s' % (self.rtrTournURL), "res_mods/0.9.5/scripts/client/mods/msg-ctr/secondary-tourney.xml")
      except:
        self.SecondaryTToggle = 'OFF'
        LOG_ERROR('Unable to download secondary tournament details from %s' % (self.rtrTournURL))

#####################################################################
# Parse secondary tournament message file
      self.tourneyMsgXML = ResMgr.openSection('scripts/client/mods/msg-ctr/secondary-tourney.xml')
      if self.tourneyMsgXML is not None:
        self.msgEnabledSTourney = self.tourneyMsgXML.readString('Show_Tourney_Message').strip().lower()
        self.msgSTourney = self.tourneyMsgXML.readString('Tournament_Battles_Message')
        LOG_NOTE('secondary-tourney.xml read successfully values are: \nSecondary Tourney Details: %s \nEnabled: %s' % (self.msgSTourney, self.msgEnabledSTourney))
      else:
        LOG_ERROR('Unable to read secondary-tourney.xml, values are: \nSecondary TourneyDetails: %s \nEnabled: %s' % (self.msgSTourney, self.msgEnabledSTourney))
      LOG_NOTE('Success!')

#####################################################################
# Combine primary and secondary tournament messages if required
      if self.combineTourney == 'yes':
        if self.msgEnabledTourney == 'yes' and self.msgEnabledSTourney == 'yes':
#          LOG_NOTE('Primary Tourney Enabled: %s and Secondary Tourney Enabled: %s' % (self.msgEnabledTourney, self.msgEnabledSTourney))
          LOG_NOTE('Combining primary and secondary tournament messages')
          self.msgTourney = self.msgTourney + '\n\n' + self.MsgDivider + '\n\n' + self.msgSTourney
        elif self.msgEnabledTourney == 'no' and self.msgEnabledSTourney == 'yes':
          LOG_NOTE('Primary tournament message is disabled, using secondary message instead')
          self.msgTourney = self.msgSTourney
        else:
          LOG_ERROR("Secondary tournament messages are disabled")
      elif self.combineTourney == 'no':
        if self.msgEnabledTourney == 'yes' and self.msgEnabledSTourney =='yes':
          LOG_NOTE('Tournament message combining is disabled, replacing primary message with secondary')
          self.msgTourney = self.msgSTourney
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
        urllib.urlretrieve('%s' % (self.rtrCWarsURL), "res_mods/0.9.5/scripts/client/mods/msg-ctr/secondary-clan-wars.xml")
      except:
        self.SecondaryCWToggle = 'OFF'
        LOG_ERROR('Unable to download secondary clan wars details from %s' % (self.rtrCWarsURL))

#####################################################################
# Parse secondary clan wars message file
      self.CWMsgXML = ResMgr.openSection('scripts/client/mods/msg-ctr/secondary-clan-wars.xml')
      if self.CWMsgXML is not None:
        self.msgEnabledSCW = self.CWMsgXML.readString('Show_Clanwars_Message').strip().lower()
        self.msgSCWmsg = self.CWMsgXML.readString('Clan_Wars_Message')
        LOG_NOTE('Successfully read secondary-clan-wars.xml values are: \nSecondary Clanwars Details: %s \nEnabled: %s' % (self.msgSCWmsg, self.msgEnabledSCW))
      else:
        LOG_ERROR('Unable to read secondary-clan-wars.xml, values are: \nSecondary Clanwars Details: %s \nEnabled: %s' % (self.msgSCWmsg, self.msgEnabledSCW))
      LOG_NOTE('Success!')

#####################################################################
# Combine primary and secondary CW messages if required
      if self.combineCW == 'yes':
        if self.msgEnabledCW == 'yes' and self.msgEnabledSCW == 'yes':
          LOG_NOTE('Combining primary and secondary clanwars messages')
          self.msgCWmsg = self.msgCWmsg + '\n\n' + self.MsgDivider + '\n\n' + self.msgSCWmsg
        elif self.msgEnabledCW == 'no' and self.msgEnabledSCW == 'yes':
          LOG_NOTE('Primary clanwars message is disabled, using secondary message instead')
          self.msgCWmsg = self.msgSCWmsg
        else:
          LOG_ERROR("Secondary clanwars message disabled")
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
      LOG_NOTE('\nself.msgTime is %s \nself.nowTime: %s \nself.difTime: %s' % (self.msgTime, self.nowTime, self.difTime))
      BigWorld.flushPythonLog()

    if self.initialMSG == True:
      self.msgTime = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))
      LOG_NOTE('sending initial message')
      BigWorld.flushPythonLog()
      self.initialMSG = False
      self.messaging()
    elif self.difTime >= self.CheckTimer:
      LOG_NOTE('self.difTime is greater than %s' % (self.CheckTimer))
      BigWorld.flushPythonLog()
      self.msgTime = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))
      self.erase()
      self.retrievePrimary()
      self.retrieveSecondaryT()
      self.retrieveSecondaryCW()
      self.messaging()
    else:
      LOG_NOTE('self.difTime is less than %s' % (self.CheckTimer))
      BigWorld.flushPythonLog()

#######################################################
# Purge Existing Messages For Re-Check
  def erase(self):
    ResMgr.purge('scripts/client/mods/msg-ctr/primary.xml')
    ResMgr.purge('scripts/client/mods/msg-ctr/secondary-tourney.xml')
    ResMgr.purge('scripts/client/mods/msg-ctr/secondary-clan-wars.xml')
    self.sys_msg = ''
    LOG_NOTE('Purged primary.xml')

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
      self.sys_msg = self.sys_msg + self.MsgHeader + '<br>' + self.MsgDivider + '<b>Unable to check for notifications</b>'
#######################################################
# If all checks were successful, present user with messages
    if self.PrimaryToggle == 'ON':
      LOG_NOTE('Telling user messages')
      self.type = SystemMessages.SM_TYPE.GameGreeting
      self.sys_msg = self.sys_msg + self.MsgHeader + '<br>' + self.MsgDivider
      if self.msgMOTDEnabled == 'yes':
        self.sys_msg = self.sys_msg + '<br><br><font color="#' + self.MOTDcolor + '"><b>' + self.msgMOTDmsg + '</b></font>'
      if self.AuthorEnabled == 'yes':
        self.sys_msg = self.sys_msg + ' -- ' + '<font color="#' + self.authorColor + '">' + self.Author + '</font><br><br>' + self.MsgDivider
      else:
        self.sys_msg = self.sys_msg + '<br><br>' + self.MsgDivider
      if self.msgMEnabled == 'yes':
        self.sys_msg = self.sys_msg + '<br><br><font color="#' + self.MeetingColor + '">' + self.msgMeeting + '</font><br><br>' + self.MsgDivider
      if self.msgEnabledTourney == 'yes' or self.msgEnabledSTourney == 'yes':
        self.sys_msg = self.sys_msg + '<br><br><font color="#' + self.Tourney_Color + '">' + self.msgTourney + '</font><br><br>' + self.MsgDivider
      if self.msgEnabledCW == 'yes' or self.msgEnabledSCW == 'yes':
        self.sys_msg = self.sys_msg + '<br><br><font color="#' + self.CWColor + '">' + self.msgCWmsg + '</font><br><br>' + self.MsgDivider
      if self.msgMOTDEnabled != 'yes' and self.msgMEnabled != 'yes' and self.msgEnabledTourney != 'yes' and self.msgEnabledCW != 'yes' and self.msgEnabledSTourney != 'yes' and self.msgEnabledSCW !='yes':
        self.sys_msg = self.sys_msg + '<br><br><font color="#FFCC00"><b>' + self.PlaceHolder + '</b></font><br><br>'
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













