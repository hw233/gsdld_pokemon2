#-*-coding:utf-8-*-
import types
import inspect
import sys
import os
#who有可能是None


#
# ========== 猎人热更模块 ===========
# 正常能用 还是不能解决 热更挂在在Game对象上的rpc mgr对象， 先这样后续解决
#



# glListDir=os.listdir("")
def Update(sModpath):
    global gbUnbind
    print("----------------sModpath",sModpath)
#	glListDir=os.listdir("Data/Py")
    sPyFile=sModpath+".py"

    mod=Import(sModpath)

    # if IsMainServer() and IsInnerServer():
    # 	GenPyc(mod)

    #记录旧的名称空间
    oldNameSpace={}
    for sName in dir(mod):
        if sName=="C_SaveObj":
            #print(Language("记录旧的名称空间时,内建扩展类，不记录:"),sName)
            continue

        obj = getattr(mod,sName)
        if inspect.isbuiltin(obj)	:
            #print(Language("记录旧的名称空间时,内建模块不记录:"),sName)
            continue

        if type(obj) in (types.FunctionType,types.ClassType, types.TypeType):
            oldNameSpace[sName]=obj
            #print(Language("记录旧的名称空间时,是要记录的："),sName)
        else:
            #print(Language("记录旧的名称空间时,不记录："),sName)
            pass

    dInfo={}
    RecordOldFunc(mod,dInfo)	#备份内存中已有的函数
    reload(mod)	#重新加载模块
    ResumeOldFunc(mod,dInfo)
    # import pprint
    # pprint.pprint(dInfo)

    #把旧对象替换回到原来的名称空间去
    for sName,oldObj in oldNameSpace.items():
        if getattr(mod,sName,None):
            ResumeOldObj(oldObj,getattr(mod,sName))
        setattr(mod,sName,oldObj)

    if hasattr(mod,"OnHotUpdate"):
        mod.OnHotUpdate()


    return True

#对象记录到名称空间
def ResumeOldObj(oldObj,newObj):	
    for sName, attr in newObj.__dict__.items():
        if sName in ('__doc__','__dict__',):
            continue
        if type(attr)==types.MemberDescriptorType:
            continue
        #print(sName)
        setattr(oldObj,sName,attr)



#备份内存中已有的函数
def RecordOldFunc(obj,dInfo):
    for sName in dir(obj):
        newobj = getattr(obj,sName)
        t=type(newobj)
        # print(t, sName)
        if t==types.FunctionType:
            dInfo[sName]=newobj
        elif t==types.MethodType:
            dInfo[sName]=newobj.im_func
        elif t ==types.ClassType:#旧风格的类
            dInfo[sName]={}
            RecordOldFunc(newobj,dInfo[sName])
        elif t==types.TypeType and sName.startswith('G'):#新风格的类是	TypeType，暂时用名字来区分
            dInfo[sName]={}
            RecordOldFunc(newobj,dInfo[sName])
        elif t==types.TypeType and sName.startswith('S'):#新风格的类是	TypeType，暂时用名字来区分
            dInfo[sName]={}
            RecordOldFunc(newobj,dInfo[sName])
#还原旧有的函数
def ResumeOldFunc(obj,dInfo):
    for sName in dir(obj):
        if sName not in dInfo:
            continue
        newobj = getattr(obj,sName)
        t=type(newobj)
        # print(sName, t)
        if t==types.FunctionType:
            DealFunction(dInfo[sName],newobj)
        elif t==types.MethodType:
            DealFunction(dInfo[sName],newobj.im_func)
        elif t==types.ClassType:
            ResumeOldFunc(newobj,dInfo[sName])
        elif t==types.TypeType and sName.startswith('G'):#没有办法找出新风格类的特点，从类名上来区分吧
            # print("resume sssssssssssssssssss sName")
            ResumeOldFunc(newobj,dInfo[sName])
        elif t==types.TypeType and sName.startswith('S'):#没有办法找出新风格类的特点，从类名上来区分吧
            ResumeOldFunc(newobj,dInfo[sName])


def DealFunction(oldFunc,newFunc): 
    for sName in dir(newFunc):
        if not sName.startswith('func_'):#只处理这类属性'func_closure', 'func_code', 'func_defaults', 'func_dict', 'func_doc', 'func_globals', 'func_name'
            continue
        if sName in ("func_closure","func_globals"):#这是只读的
            continue
        attr=getattr(newFunc,sName)
        setattr(oldFunc,sName,attr)

#查找模块，返回模块的所有属性
def Import(sPath):
    mod=__import__(sPath)
    lPart=sPath.split('.')    
    for sPart in lPart[1:]:
        mod=getattr(mod,sPart)
    return mod			
    
def GenPyc(mod):
    #内服防止生成pyc时申请内存超出32位限制，调命令生成
    try:
        import os,platform
        FileName=os.path.abspath(mod.__file__)
        FileName=FileName.replace(".pyc",".py")
        if platform.system().upper()=="WINDOWS":
            os.system("python -m py_compile %s"%FileName)
        else:
            os.system("python2.5 -m py_compile %s"%FileName) #这个命令只在测试服能用
    except:
        LogPyException()

gsUpdateFile="update.log"
    
# if IsMainServer():
# 	gsFileName="NeedUpdateFile.text"#需热更新的文件列表
# elif IsPublicServer():
# 	gsFileName="NeedUpdateFilePs.text"
# else:
# 	gsFileName="NeedUpdateFile2.text"

    
glNeedUpdateFile=[]
#定时导入待更新列表
def ReadAndUnlink():	

    if not os.path.exists(gsFileName):
        return
    try:
        global gbUpdateScript
        global gbUnbind
        f = open(gsFileName, 'r')
        sText = f.read()
        f.close()
        os.unlink(gsFileName)
        global glCurrentNeedUpdateFile
        glCurrentNeedUpdateFile = {}

        if os.path.exists(gsUpdateFile):#删掉上次的文件
            os.unlink(gsUpdateFile)

        for sLine in sText.split("\n"):
            if not sLine or sLine[0]=="#":#空行或注释
                continue
            sNewLine=sLine.strip()
            if len(sNewLine):
                glNeedUpdateFile.append(sNewLine)
                glCurrentNeedUpdateFile[sNewLine]=sNewLine


        if glNeedUpdateFile and not FindCallLater("DoAutoUpdate"):
            global glDetailedUpdateFile
            glDetailedUpdateFile=[]
            DoAutoUpdate()
    except:
        LogPyException()

#自动更新
def DoAutoUpdate():
    if not glNeedUpdateFile:
        return
    global gbUpdateScript
    sLine=glNeedUpdateFile.pop(0)
    if glNeedUpdateFile:
        CallLater(DoAutoUpdate,3,"DoAutoUpdate")#3秒钟后更新下一行

    l=[]
    global glDetailedUpdateFile
    global glCurrentNeedUpdateFile
    global gbUnbind
    lUpdate=[]
    sDir = os.getcwd()
    try:
        for sPyFile in sLine.split(";"):#,一行内可以有多个文件,多个文件间用分号;分隔
            fStamp=time.time()
            iFlag = Update(None,sPyFile)
            if not iFlag:
                continue
            iCost=(time.time()-fStamp)*1000
            l.append("update %s,cost %d"%(sPyFile,iCost))
            lUpdate.append("%s %s %d"%(ChangeToDateTime(),sDir+"/"+sPyFile,iCost))
            if sPyFile in glCurrentNeedUpdateFile:
                glDetailedUpdateFile.append(sPyFile)
    except:
        LogPyException()
    if l:
        Log2File("_AutoUpdateResult",";".join(l))

    #写入文件，方便运维查看
    try:
        f2 = open("update.log","a")
        for info in lUpdate:
            f2.write(str(info)+"\n")
        f2.close()
    except:
        LogPyException()


# def AfterFirstImport():    
# 	ReadAndUnlink()

if "glDetailedUpdateFile" not in globals():
    glDetailedUpdateFile=[]

if "glCurrentNeedUpdateFile" not in globals():
    glCurrentNeedUpdateFile={}

if "gbUpdateScript" not in  globals():
    gbUpdateScript=False#标识是否热更script
    gbUnbind=False

def getGlDetailedUpdateFile():
    global glDetailedUpdateFile
    return glDetailedUpdateFile

def LogPyException():
    print("--------------------LogPyException")

# import notify
import os
import time
import os.path
# import init
# from utility import *
# import timecalc