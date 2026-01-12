#!/usr/bin/env python3

import os, shutil
from xdg import DesktopEntry

#######################

class getMenu():
    
    def __init__(self, _item):
        self._item = _item
        # removed "Audio" e "Video" main categories
        self.freedesktop_main_categories = ["AudioVideo","Development", 
                                    "Education","Game","Graphics","Network",
                                    "Office","Settings","System","Utility"]
        # additional categories
        self.development_extended_categories = ["Building","Debugger","IDE","GUIDesigner",
                                    "Profiling","RevisionControl","Translation",
                                    "Database","WebDevelopment"]
        
        self.office_extended_categories = ["Calendar","ContanctManagement","Office",
                                    "Dictionary","Chart","Email","Finance","FlowChart",
                                    "PDA","ProjectManagement","Presentation","Spreadsheet",
                                    "WordProcessor","Engineering"]
        
        self.graphics_extended_categories = ["2DGraphics","VectorGraphics","RasterGraphics",
                                    "3DGraphics","Scanning","OCR","Photography",
                                    "Publishing","Viewer"]
        
        self.utility_extended_categories = ["TextTools","TelephonyTools","Compression",
                                    "FileTools","Calculator","Clock","TextEditor",
                                    "Documentation"]
        
        self.settings_extended_categories = ["DesktopSettings","HardwareSettings",
                                    "Printing","PackageManager","Security",
                                    "Accessibility"]
        
        self.network_extended_categories = ["Dialup","InstantMessaging","Chat","IIRCClient",
                                    "FileTransfer","HamRadio","News","P2P","RemoteAccess",
                                    "Telephony","VideoConference","WebBrowser"]
        
        # added "Audio" and "Video" main categories
        self.audiovideo_extended_categories = ["Audio","Video","Midi","Mixer","Sequencer","Tuner","TV",
                                    "AudioVideoEditing","Player","Recorder",
                                    "DiscBurning"]
        
        self.game_extended_categories = ["ActionGame","AdventureGame","ArcadeGame",
                                    "BoardGame","BlockGame","CardGame","KidsGame",
                                    "LogicGame","RolePlaying","Simulation","SportGame",
                                    "StrategyGame","Amusement","Emulator"]
        
        self.education_extended_categories = ["Art","Construction","Music","Languages",
                                    "Science","ArtificialIntelligence","Astronomy",
                                    "Biology","Chemistry","ComputerScience","DataVisualization",
                                    "Economy","Electricity","Geography","Geology","Geoscience",
                                    "History","ImageProcessing","Literature","Math","NumericAnalysis",
                                    "MedicalSoftware","Physics","Robots","Sports","ParallelComputing",
                                    "Electronics"]
        
        self.system_extended_categories = ["FileManager","TerminalEmulator","FileSystem",
                                    "Monitor","Core"]
        #
        # arguments in the exec fiels
        # self.execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
        self.execArgs = ["%f", "%F", "%u", "%U", "%d", "%D", "%n", "%N", "%k", "%v"]
        #
        self.list = []
        self.fpop()
    
#############################

    def fpop(self):
        file_path = self._item
        try:
            entry = DesktopEntry.DesktopEntry(file_path)
            ftype = entry.getType()
            if ftype != "Application":
                return
            #
            ftry = entry.getTryExec()
            if ftry:
                if not shutil.which(ftry):
                    return
            #
            hidden = entry.getHidden()
            nodisplay = entry.getNoDisplay()
            # do not show those marked as hidden or not to display
            if hidden or nodisplay:
                return
            # item.name
            fname = entry.getName()
            # item.path
            # fpath
            # category
            ccat = entry.getCategories()
            fcategory = self.get_category(ccat)
            ## item.name.lower()
            # fname_lower = fname.lower()
            # pexec (executable)
            fexec = entry.getExec()
            # if fexec[0] == '"':
                # fexec = fexec.lstrip('"').rstrip('"')
            if fexec[0:5] == "$HOME":
                fexec = "~"+fexec[5:]
            # check for arguments and remove them
            # # # if fexec[-3:] in self.execArgs:
                # # # fexec = fexec[:-3]
            # # for aargs in self.execArgs:
                # # if aargs in fexec:
                    # # fexec = fexec.strip(aargs)
            # fexec = fexec.split(" ")[0]
            fexec_temp = fexec.split(" ")
            for targ in self.execArgs:
                if targ in fexec_temp:
                    fexec_temp.remove(targ)
            fexec = " ".join(fexec_temp)
            # icon
            ficon = entry.getIcon()
            # comment
            fcomment = entry.getComment()
            # tryexec
            fpath = entry.getPath()
            # terminal
            fterminal = entry.getTerminal()
            ###
            # if not self.menu_prog:
                # file_fpath = ""
            # else:
            file_fpath = file_path
            #
            self.list = [fname, fcategory or "Missed", fexec, ficon, fcomment, fpath, fterminal, file_fpath]
        except:
            pass
    
    #
    def get_category(self, ccat):
        if ccat == []:
            return "Missed"
        for cccat in ccat:
            # search in the main categories first
            if cccat in self.freedesktop_main_categories:
                # from AudioVideo to Multimedia
                if cccat == "AudioVideo":
                    return "Multimedia"
                return cccat
            elif cccat in self.development_extended_categories:
                return "Development"
            elif cccat in self.office_extended_categories:
                return "Office"
            elif cccat in self.graphics_extended_categories:
                return "Graphics"
            elif cccat in self.utility_extended_categories:
                return "Utility"
            elif cccat in self.settings_extended_categories:
                return "Settings"
            elif cccat in self.network_extended_categories:
                return "Network"
            elif cccat in self.audiovideo_extended_categories:
                #return "AudioVideo"
                return "Multimedia"
            elif cccat in self.game_extended_categories:
                return "Game"
            elif cccat in self.education_extended_categories:
                return "Education"
            elif cccat in self.system_extended_categories:
                return "System"


# ret = getMenu('/home/linux/.local/share/applications/alacarte-made-1.desktop')
# print(ret.list)
