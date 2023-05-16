from nis import match
from sys import argv
from codecs import open
from re import compile
from copy import copy
import os

re_translation = compile(r'^"(.+)" = "(.+)";$')
re_comment_single = compile(r'^/\*.*\*/$')
re_comment_start = compile(r'^/\*.*$')
re_comment_end = compile(r'^.*\*/$')
 
class LocalizedString():
    def __init__(self, translation):
        self.translation = translation
        self.key, self.value = re_translation.match(self.translation).groups()
 
    def __unicode__(self):
        return u'%s\n' % (self.translation)
 
class LocalizedFile():
    def __init__(self, fname=None, auto_read=False):
        self.fname = fname
        self.strings = []
        self.strings_d = {}
 
        if auto_read:
            self.read_from_file(fname)
 
    def read_from_file(self, fname=None):
        fname = self.fname if fname == None else fname
        try:
            f = open(fname, encoding='utf-8', mode='r', errors='ignore')
        except:
            print ('File %s does not exist.' % fname)
            exit(-1)
        
        line = f.readline().replace('\x00','')
        while line:
            # comments = [line]
            # if not re_comment_single.match(line):
            #     while line and not re_comment_end.match(line):
            #         line = f.readline().replace('\x00','')
            #         comments.append(line.replace('\r\n', ''))
             
            # line = f.readline().replace('\x00','')
            # if line and re_translation.match(line):
            #     translation = line
            # else:
            #     raise Exception('invalid file')
             
            # line = f.readline()
            # while line and line == u'\n':
            #     line = f.readline()
            
            if line.endswith(';\n'):
                line_compare = line.removesuffix('\n')
            elif line.endswith(';\r\n'):
                line_compare = line.removesuffix('\r\n')
            else:
                line_compare = line
            
            if line_compare and re_translation.match(line_compare):
                string = LocalizedString(line_compare)
                self.strings.append(string)
                self.strings_d[string.key] = string

            line = f.readline().replace('\x00','')
 
        f.close()
 
    def save_to_file(self, fname=None):
        fname = self.fname if fname == None else fname
        try:
            f = open(fname, encoding='UTF-8', mode='w', errors='ignore')
        except:
            print ('Couldn\'t open file %s.' % fname)
            exit(-1)
 
        for string in self.strings:
            f.write(string.__unicode__())
 
        f.close()
 
    def merge_with(self, new):
        merged = LocalizedFile()
 
        for string in new.strings:
            if self.strings_d.__contains__(string.key):
                new_string = copy(self.strings_d[string.key])
                string = new_string

            print ('MERGE: %s' % string.key)
            merged.strings.append(string)
            merged.strings_d[string.key] = string
 
        return merged
    
    def replace_with(self, new):
        merged = LocalizedFile()

        for string in self.strings:
            if new.strings_d.__contains__(string.key):
                new_string = copy(new.strings_d[string.key])
                string = new_string

            print ('REPLACE: %s' % string.key)
            merged.strings.append(string)
            merged.strings_d[string.key] = string
 
        return merged

    # def merge_with_jp(self, new):
    #     merged_old = LocalizedFile()
    #     merged_new = LocalizedFile()
    #     merged = LocalizedFile()

    #     for string in new.strings:
    #         if self.strings_d.__contains__(string.key):
    #             new_string = copy(self.strings_d[string.key])
    #             string = new_string
    #             print ('MERGE OLD: %s' % string.key)
    #             merged_old.strings.append(string)
    #             merged_old.strings_d[string.key] = string
    #         else:
    #             print ('MERGE NEW: %s' % string.key)
    #             merged_new.strings.append(string)
    #             merged_new.strings_d[string.key] = string

    #     for oldString in merged_old.strings:
    #         merged.strings.append(oldString)
    #         merged.strings_d[oldString.key] = oldString

    #     for newString in merged_new.strings:
    #         merged.strings.append(newString)
    #         merged.strings_d[newString.key] = newString

    #     return merged
 
def merge(output_fname, old_fname, new_fname):
    try:
        old = LocalizedFile(old_fname, auto_read=True)
        new = LocalizedFile(new_fname, auto_read=True)
        merged = old.merge_with(new)
        merged.save_to_file(output_fname)
    except ValueError as err:
        print ('Error: input files have invalid format. %s' % err)

def replace(output_fname, old_fname, new_fname):
    try:
        old = LocalizedFile(old_fname, auto_read=True)
        new = LocalizedFile(new_fname, auto_read=True)
        replace = old.replace_with(new)
        replace.save_to_file(output_fname)
    except ValueError as err:
        print ('Error: input files have invalid format. %s' % err)

# def merge_jp(merged_fname, old_fname, new_fname):
#     try:
#         old = LocalizedFile(old_fname, auto_read=True)
#         new = LocalizedFile(new_fname, auto_read=True)
#         merged = old.merge_with_jp(new)
#         merged.save_to_file(merged_fname)
#     except ValueError as err:
#         print ('Error: input files have invalid format. %s' % err)
 
 
STRINGS_FILE = 'Localizable.strings'
EXCEPTION_FOLDER = {"Pods", "Settings.bundle"}
GENSTRING_RESULT_FOLDER = 'genstring_results'

def localizeCode(path):
    print ('Localize source code at path: %s ...' % path)
    path_queue = [os.path.join(path, name) for name in os.listdir(path) if name != "Pods"]
    lproj_queue = []
    while len(path_queue) != 0:
        p = path_queue.pop()
        if os.path.basename(p) in EXCEPTION_FOLDER:
            continue

        print ('Scan folder: %s' % p)
        if os.path.isdir(p):
            dir_name = os.path.basename(p)
            if dir_name.endswith('.lproj'):
                lproj_queue.append(p)
            else:
                new_dir_s = [os.path.join(p, name) for name in os.listdir(p)]
                path_queue.extend(new_dir_s)

    # create folder result
    result_path = os.path.join(os.path.curdir, GENSTRING_RESULT_FOLDER)
    if os.path.exists(result_path):
        os.system('rm -d %s' % GENSTRING_RESULT_FOLDER)
    os.system('mkdir -p %s' % GENSTRING_RESULT_FOLDER)

    # genstrings
    os.system('genstrings -q -o "%s" `find %s -name "*.swift" -o -name "*.m"`' % (result_path, path))

    # Scan lproj folders
    

    # languages = [lang for lang in [os.path.join(path, name) for name in os.listdir(path)]
    #             if lang.endswith('.lproj') and os.path.isdir(lang)]
    # print (os.listdir(path))
    # for language in languages:
    #     print (language)
        # original = merged = os.path.join(language, STRINGS_FILE)
        # old = original + '.old'
        # new = original + '.new'
     
        # if os.path.isfile(original):
        #     os.rename(original, old)
        #     os.system('genstrings -q -s %s -o "%s" `find %s -name "*.swift" -o -name "*.m"`' % (routine, language, path))
        #     os.system('iconv -f UTF-16 -t UTF-8 "%s" > "%s"' % (original, new))
        #     merge(merged, old, new)
        # else:
        #     os.system('genstrings -q -s %s -o "%s" `find %s -name "*.swift" -o -name "*.m"`' % (routine, language, path))
        #     os.rename(original, old)
        #     os.system('iconv -f UTF-16 -t UTF-8 "%s" > "%s"' % (old, original))
         
        # if os.path.isfile(old):
        #     os.remove(old)
        # if os.path.isfile(new):
        #     os.remove(new)
 
# def localizeInterface(path, developmentLanguage):
#     baseDir = os.path.join(path, "Base.lproj")
#     developmentLanguage = os.path.splitext(developmentLanguage)[0] + ".lproj" # Add the extension if not exists
#     print (developmentLanguage)
#     if os.path.isdir(baseDir):
#         print ('Localize interface...')
#         ibFileNames = [name for name in os.listdir(baseDir) if name.endswith('.storyboard') or name.endswith('.xib')]
#         languages = [lang for lang in [os.path.join(path, name) for name in os.listdir(path)]
#                     if lang.endswith('.lproj') and not lang.endswith('Base.lproj') and os.path.isdir(lang)]
#         for language in languages:
#             print (language)
#             for ibFileName in ibFileNames:
#                 ibFilePath = os.path.join(baseDir, ibFileName)
#                 stringsFileName = os.path.splitext(ibFileName)[0] + ".strings"
#                 print ('  ' + stringsFileName)
#                 original = merged = os.path.join(language, stringsFileName)
#                 old = original + '.old'
#                 new = original + '.new'
                
#                 if os.path.isfile(original) and not language.endswith(developmentLanguage):
#                     os.rename(original, old)
#                     os.system('ibtool --export-strings-file %s %s' % (original, ibFilePath))
#                     os.system('iconv -f UTF-16 -t UTF-8 "%s" > "%s"' % (original, new))
#                     merge(merged, old, new)
#                 else:
#                     os.system('ibtool --export-strings-file %s %s' % (original, ibFilePath))
#                     os.rename(original, old)
#                     os.system('iconv -f UTF-16 -t UTF-8 "%s" > "%s"' % (old, original))
                    
#                 if os.path.isfile(old):
#                     os.remove(old)
#                 if os.path.isfile(new):
#                     os.remove(new)

if __name__ == '__main__':
    argc = len(argv)
    if argc < 2:
        print ("invalid arguments")
        quit()

    function_name = argv[1]
    print (function_name)
    if function_name == "-merge":
        if argc != 4:
            print ("function arguments is invalid")
        else:
            old_localizable_path = os.path.abspath(argv[2])
            new_localizable_path = os.path.abspath(argv[3])
            output_localizable_path = os.path.abspath(argv[4])
            merge(output_localizable_path, old_localizable_path, new_localizable_path)
    elif function_name == "-replace":
        if argc != 4:
            print ("function arguments is invalid")
        else:
            old_localizable_path = os.path.abspath(argv[2])
            new_localizable_path = os.path.abspath(argv[3])
            output_localizable_path = os.path.abspath(argv[4])
            replace(output_localizable_path, old_localizable_path, new_localizable_path)
    elif function_name == "-genstrings":
        if argc != 3:
            print ("function arguments is invalid")
        else:
            localizeCode(argv[2])
    else:
        print ("function is invalid")
