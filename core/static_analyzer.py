import r2pipe
import json
import base64
import math
from nltk import ngrams
import functools 


def get_ngrams(opcodes, n_ngram):
   return ngrams(opcodes, n_ngram)

def jaccard_index(a,b):
    if a != None and b != None:
      
        return float(len(set(a).intersection(b)))/len(set(a).union(b))*100
    else:
        return 0

def get_num_func_cc(func_dict_cc):
    func_cc_count = {}
    if func_dict_cc is not None:
        for i in func_dict_cc:
            try:
                func_cc_count[func_dict_cc[i]] +=1
            except:
                func_cc_count[func_dict_cc[i]] = 1
        return func_cc_count
    return None

def structural_similarity(a,b):
    sample_a = get_num_func_cc(a)
    sample_b = get_num_func_cc(b)

    distance = []
    if sample_a is not None and sample_b is not None:
        for i in sample_a:
            if i in sample_b:
                distance.append(min(sample_a[i],sample_b[i])/max(sample_a[i],sample_b[i]))

        for i in sample_b:
            if i not in sample_a:
                distance.append(0)

        return (functools.reduce(lambda a,b: a+b,distance)/len(distance))*100
    return 0

class StaticAnalysis():
    def __init__(self, file):
        self.r2_handler = r2pipe.open(file, flags=['-2'])
        self.r2_handler.cmd('e anal.timeout = {}'.format(60))

    #def __del__(self):
    #    self.r2_handler.quit()

    def get_info_file(self):
        return json.loads(self.r2_handler.cmd('ij'))

    def get_sections(self):
        sections_array = []
        try:
            sections = json.loads(self.r2_handler.cmd('iSj entropy'))['sections']

            for section in sections:

                section_dic = {}
                if 'name' in section:
                    section_dic['name'] = section['name']
                if 'entropy' in section:
                    section_dic['entropy'] = section['entropy']
                if 'perm' in section:
                    section_dic['perm'] = section['perm']
                if 'size' in section:
                    section_dic['size'] = section['size']

                sections_array.append(section_dic)
        except:
            pass
        return sections_array

    def get_imports(self):
        imports = json.loads(self.r2_handler.cmd('iij'))
        func_name_imp = list(map(lambda x: x['name'], imports))
        return func_name_imp

    def get_libs(self):
        libs = json.loads(self.r2_handler.cmd('ilj'))
        return libs

    def get_hash_file(self):
        hashes = json.loads(self.r2_handler.cmd('e bin.hashlimit=100M; itj'))
        return hashes

    def get_data_strings(self):
        strings = json.loads(self.r2_handler.cmd('izj'))
        return list(map(lambda x: base64.b64decode(x['string']), strings))

    def get_list_func(self):
        try:
            self.r2_handler.cmd('aaa')
            func_list = json.loads(self.r2_handler.cmd('aflj'))
            func_list = list(map(lambda x: x['name'], func_list))
        except:
            func_list =[]
        return func_list

    def get_opcodes_func(self,func):
        if 'imp' not in func:
            try:
                opcodes = json.loads(self.r2_handler.cmd('s ' + func + "; pdfj"))
                opcodes = list(filter(lambda x: 'opcode' in x, opcodes['ops']))
                opcodes = list(map(lambda x: x['opcode'].split(' ')[0], opcodes))
                return opcodes
            except:
                return -1



    def get_complexity_cyclomatic(self,func):
        if 'imp' not in func:
            try:
                func_cc = json.loads(self.r2_handler.cmd('s ' + func + "; afCc"))
                return func_cc
            except:
                return ""

        


class Elf:

    def __init__(self, file):
        self.static_analysis = StaticAnalysis(file)
        self.arch = None
        self.machine = None
        self.bits = None
        self.bintype = None
        self.compiler = None
        self.stripped = None
        self.endian = None
        self.sections = None
        self.imports = None
        self.libs = None
        self.md5 = None
        self.sha1 = None
        self.cc = None
        self.opcodes_func = None
        self.n_grams = None
        self.func_list = None
    def information_file(self):
        binary_info = self.static_analysis.get_info_file()
        if 'bin' not in binary_info:
            print("No es un archivo EXECutable!!!!")
            return

        self.arch = binary_info['bin']['arch']
        self.machine = binary_info['bin']['machine']
        self.bits = binary_info['bin']['bits']
        self.bintype = binary_info['bin']['bintype']
        self.compiler = binary_info['bin']['compiler']
        self.stripped = ''#binary_info['bin']['stripped']
        self.endian = binary_info['bin']['endian']

    def sections_file(self):
        self.sections = self.static_analysis.get_sections()

    def imports_file(self):
        self.imports = self.static_analysis.get_imports()

    def libs_file(self):
        self.libs = self.static_analysis.get_libs()

    def hash_file(self):
        hashes = self.static_analysis.get_hash_file()
        self.md5 = hashes['md5']
        self.sha1 = hashes['sha1']

    def get_function_list(self):
        self.func_list = self.static_analysis.get_list_func()

    def get_cyclomatic_complexity(self):
        self.cc = {}
        for func in self.func_list:
            cc_func = self.static_analysis.get_complexity_cyclomatic(func)
            if cc_func != "":
                self.cc[func] = cc_func

    def get_opcodes_func(self):
        self.opcodes_func = {}
        for func in self.func_list:
            opcodes_f = self.static_analysis.get_opcodes_func(func)
            if opcodes_f != -1 and opcodes_f != None:
                self.opcodes_func[func] = opcodes_f

    def get_ngrams(self):
        self.n_grams = []
        for func in self.opcodes_func:
            if func in self.opcodes_func:
                self.n_grams.extend(list(get_ngrams(self.opcodes_func[func], 6)))

    def stadistical_bb(self):
        pass

    def get_strings(self):
        self.strings = self.static_analysis.get_data_strings()

    def dump_to_dict(self):
        elf_dict = dict()
        elf_dict['arch'] = self.arch 
        elf_dict['machine'] = self.machine
        elf_dict['bits'] = self.bits
        elf_dict['bintype'] = self.bintype
        elf_dict['compiler'] = self.compiler
        # elf_dict['stripped'] = self.stripped
        elf_dict['endian'] = self.endian
        elf_dict['sections'] = self.sections
        elf_dict['imports'] = self.imports
        elf_dict['libs'] = self.libs
        elf_dict['md5'] = self.md5
        elf_dict['sha1'] = self.sha1
        elf_dict['cc'] = self.cc
        elf_dict['opcodes_func'] = self.opcodes_func
        # elf_dict['n_grams'] = self.n_grams
        return elf_dict

