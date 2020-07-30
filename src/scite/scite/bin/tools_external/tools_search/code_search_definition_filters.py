# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

c_exts = ['.c', '.cc', '.cpp', '.cxx', '.h', '.hh', '.hpp', '.hxx']

def killAllWithinMatching(s, startChar='(', endChar=')'):
    level = 0
    output = ''
    for ch in s:
        if ch == startChar:
            level += 1
        elif ch == endChar:
            level = max(0, level - 1)
        elif level == 0:
            output += ch
    return output

def killNamespaces(s):
    parts = s.split('::')
    return parts[-1]

class FilterLineAcceptsAll(object):
    def isMatch(self, text):
        return True
    
class FilterLinePythonDefinition(object):
    def __init__(self, searchTerm):
        self.searchTerm = searchTerm

    def isMatch(self, text):
        textLstr = text.lstrip()
        if textLstr.startswith('def ' + self.searchTerm + '('):
            return True
        if textLstr.startswith('class ' + self.searchTerm + '('):
            return True
        if textLstr.startswith('class ' + self.searchTerm + ':'):
            return True
        if textLstr.startswith(self.searchTerm + ' = '):
            # will possibly find many hits, user will have to look for the first.
            return True

class FilterLineCDefinition(object):
    def __init__(self, searchTerm):
        self.searchTerm = searchTerm
    
    def isMatch(self, text):
        # don't base on filetype; inline methods are often implemented in headers
        # don't base on indentation; class inline methods might be indented
        
        parts = text.split()
        containsSemicolon = ';' in text
        
        if not len(parts):
            return False
        
        if parts[0][0] == '#':
            if parts[0] == '#define' and len(parts) > 1:
                if parts[1] == self.searchTerm:
                    return True
                elif parts[1].startswith(self.searchTerm + '('):
                    return True
                    
            return False
        
        if parts[0] in ('class', 'struct', 'interface', 'enum') and len(parts) > 1:
            if parts[1] == self.searchTerm and not containsSemicolon:
                return True
            else:
                return False
        
        if parts[0] == 'typedef':
            if self.searchTerm + ';' in parts or ('*' + self.searchTerm + ';') in parts:
                return True
            else:
                return False
        
        # what is not a definition?
        # has ;
        # has operators after killing (contents) and <contents>
        # searchTerm not present after killing (contents) and <contents>
        # searchTerm not present on its own. allow searchTerm(, dissallow ->searchTerm
        # searchTerm is the first item. then it's probably a void method call. searchTerm();
        
        textFiltered = killAllWithinMatching(text, '(', ')')
        textFiltered = killAllWithinMatching(textFiltered, '<', '>')
        partsFiltered = textFiltered.split()
        partsFiltered = list(map(killNamespaces, partsFiltered))
        
        # traditional C-style const char *SearchTerm()
        for i in range(len(partsFiltered)):
            partsFiltered[i] = partsFiltered[i].lstrip('*').rstrip('[]')
        
        try:
            index = partsFiltered.index(self.searchTerm)
        except ValueError:
            # searchTerm not present, it was either in an argument, or not present on its own, e.g. ->searchTerm .searchTerm
            return False
        
        if index == 0:
            # it's probably a void method call. searchTerm();
            return False
        
        if index + 1 < len(partsFiltered) and partsFiltered[index + 1] == '=':
            # like a variable, int SearchTerm = 1234;
            return True
        
        shouldNotContain = (';', 'return', ',', '+', '-', '/', '%', '^', '|', '=', '-', '*=', '&=')
        for item in shouldNotContain:
            if item in textFiltered:
                return False
        
        return True
        

class FilterLineCDeclaration(object):
    def __init__(self, searchTerm):
        self.searchTerm = searchTerm

    def isMatch(self, text):
        parts = text.split()
        
        if not len(parts):
            return False
        
        # designed for methods and variables, will not find classes/structs/macros.
        if parts[0] in ('class', 'struct', 'interface', 'enum', '#define', 'typedef'):
            return False
        
        textFiltered = killAllWithinMatching(text, '(', ')')
        textFiltered = killAllWithinMatching(textFiltered, '<', '>')
        partsFiltered = textFiltered.split()
        # skip removing namespaces
        
        # traditional C-style const char *SearchTerm()
        for i in range(len(partsFiltered)):
            partsFiltered[i] = partsFiltered[i].lstrip('*').rstrip('[];')
        
        try:
            index = partsFiltered.index(self.searchTerm)
        except ValueError:
            # searchTerm not present, it was either in an argument, or not present on its own, e.g. ->searchTerm .searchTerm
            return False
        
        if index == 0:
            # it's probably a void method call. searchTerm();
            return False
        
        shouldNotContain = ('{', 'return', '+', '-', '/', '%', '^', '|', '=', '-', '*=', '&=')
        for item in shouldNotContain:
            if item in textFiltered:
                return False
        
        return True

def filterLine(recordedResults, line, filterObj):
    if line[1:2] == ':':
        # looks like a windows drive name, e.g. c:\file
        parts = line.split(':', 3)
        parts[1] = parts[0] + ':' + parts[1]
        parts.pop(0)
    else:
        parts = line.split(':', 2)
    
    if len(parts) != 3:
        # unsure what was printed, we'll print to stdout but not add to recordedResults
        return True
    else:
        filepath, lineno, match = parts
        if filterObj.isMatch(match):
            recordedResults.append((filepath, lineno, match))
            return True
            
    return False

def getFilterObject(action, extension, searchTerm):
    if action == 'any_whole_word':
        filetypes = '*'
        filterObj = FilterLineAcceptsAll()
    elif action == 'definition':
        if extension == '.py':
            filetypes = '*.py'
            filterObj = FilterLinePythonDefinition(searchTerm)
        elif extension in c_exts:
            filetypes = ' '.join('*' + s for s in c_exts)
            filterObj = FilterLineCDefinition(searchTerm)
        else:
            print('Search definition is only supported for Python or C.')
            return None, None
    elif action == 'declaration':
        if extension in c_exts:
            filetypes = ' '.join('*' + s for s in c_exts)
            filterObj = FilterLineCDeclaration(searchTerm)
        else:
            print('Search declaration is only supported for C.')
            return None, None
    else:
        print('Unknown action')
        return None, None
    
    return filterObj, filetypes

def assertEq(expected, received):
    if expected != received:
        raise AssertionError('expected %s but got %s' % (expected, received))

def tests():
    assertEq('abc', killAllWithinMatching('abc'))
    assertEq('abc', killAllWithinMatching('abc('))
    assertEq('ab', killAllWithinMatching('ab(c'))
    assertEq('', killAllWithinMatching('(abc'))
    assertEq('', killAllWithinMatching('(abc)'))
    assertEq('abc', killAllWithinMatching('()abc'))
    assertEq('abc', killAllWithinMatching('a()bc'))
    assertEq('abc', killAllWithinMatching('ab()c'))
    assertEq('bc', killAllWithinMatching('(a)bc'))
    assertEq('ac', killAllWithinMatching('a(b)c'))
    assertEq('ab', killAllWithinMatching('ab(c)'))
    assertEq('c', killAllWithinMatching('(ab)c'))
    assertEq('a', killAllWithinMatching('a(bc)'))
    assertEq('a', killAllWithinMatching('a((bc)other'))
    assertEq('alvl', killAllWithinMatching('a((bc)other)lvl'))
    assertEq('alvl', killAllWithinMatching('a((bc)other(bc))lvl'))
    assertEq('notbelowzero', killAllWithinMatching(')(a)notbelowzero'))
    assertEq('notbelowzero', killAllWithinMatching('))(a)notbelowzero'))
    assertEq('notbelowzero', killAllWithinMatching(')))(a)notbelowzero'))
    assertEq('notbelowzero', killAllWithinMatching('(a)))(a)notbelowzero'))
    
    assertEq('', killNamespaces(''))
    assertEq('abc', killNamespaces('abc'))
    assertEq('abc', killNamespaces('::abc'))
    assertEq('abc', killNamespaces('123::abc'))
    assertEq('abc', killNamespaces('456::123::abc'))
    assertEq('123:abc', killNamespaces('123:abc'))
    
    obj = FilterLineAcceptsAll()
    recordedResults = []
    assertEq(True, filterLine(recordedResults, 'unknown format', obj))
    assertEq(0, len(recordedResults))
    assertEq(True, filterLine(recordedResults, 'unknown:format', obj))
    assertEq(0, len(recordedResults))
    assertEq(True, filterLine(recordedResults, 'filepath:123:text', obj))
    assertEq(('filepath', '123', 'text'), recordedResults[-1])
    assertEq(True, filterLine(recordedResults, 'filepath:123:', obj))
    assertEq(('filepath', '123', ''), recordedResults[-1])
    assertEq(True, filterLine(recordedResults, 'filepath:123:text:moretext', obj))
    assertEq(('filepath', '123', 'text:moretext'), recordedResults[-1])
    assertEq(True, filterLine(recordedResults, 'Q:\\filepath:123:text', obj))
    assertEq(('Q:\\filepath', '123', 'text'), recordedResults[-1])
    assertEq(True, filterLine(recordedResults, 'C:\\filepath:123:text:moretext', obj))
    assertEq(('C:\\filepath', '123', 'text:moretext'), recordedResults[-1])
    
    obj = FilterLinePythonDefinition('SearchTerm')
    assertEq(False, bool(obj.isMatch('')))
    assertEq(False, bool(obj.isMatch('SearchTerm')))
    assertEq(False, bool(obj.isMatch('SearchTerm def ')))
    assertEq(False, bool(obj.isMatch('defSearchTerm')))
    assertEq(False, bool(obj.isMatch('def.SearchTerm')))
    assertEq(False, bool(obj.isMatch('def SearchTermF')))
    assertEq(False, bool(obj.isMatch('def SearchTerm:')))
    assertEq(False, bool(obj.isMatch('def SearchTerm')))
    assertEq(False, bool(obj.isMatch('# def SearchTerm(')))
    assertEq(True, bool(obj.isMatch('def SearchTerm(')))
    assertEq(True, bool(obj.isMatch('def SearchTerm(a, b, c')))
    assertEq(True, bool(obj.isMatch('def SearchTerm(a, b, c):')))
    assertEq(True, bool(obj.isMatch(' def SearchTerm(a, b, c):')))
    assertEq(True, bool(obj.isMatch('class SearchTerm:')))
    assertEq(True, bool(obj.isMatch('class SearchTerm(')))
    assertEq(True, bool(obj.isMatch('class SearchTerm(object)')))
    assertEq(True, bool(obj.isMatch('class SearchTerm(object):')))
    assertEq(True, bool(obj.isMatch(' class SearchTerm(object):')))
    assertEq(True, bool(obj.isMatch('SearchTerm = ')))
    assertEq(True, bool(obj.isMatch('SearchTerm = a')))
    assertEq(True, bool(obj.isMatch(' SearchTerm = a')))
    
    obj = FilterLineCDefinition('SearchTerm')
    assertEq(False, bool(obj.isMatch('')))
    assertEq(False, bool(obj.isMatch('#define. SearchTerm f')))
    assertEq(False, bool(obj.isMatch('#define')))
    assertEq(False, bool(obj.isMatch('#define SearchTermF')))
    assertEq(False, bool(obj.isMatch('#define SearchTerm:')))
    assertEq(True, bool(obj.isMatch('#define SearchTerm(')))
    assertEq(True, bool(obj.isMatch('#define SearchTerm(a, b, c)')))
    assertEq(True, bool(obj.isMatch('#define SearchTerm ')))
    assertEq(False, bool(obj.isMatch('#define not SearchTerm ')))
    assertEq(False, bool(obj.isMatch('#define not() SearchTerm ')))
    assertEq(False, bool(obj.isMatch('class SearchTermF')))
    assertEq(False, bool(obj.isMatch('class SearchTerm;')))
    assertEq(False, bool(obj.isMatch('class SearchTerm ;')))
    assertEq(False, bool(obj.isMatch('class SearchTerm()')))
    assertEq(True, bool(obj.isMatch('class SearchTerm')))
    assertEq(True, bool(obj.isMatch('enum SearchTerm')))
    assertEq(True, bool(obj.isMatch(' enum SearchTerm')))
    assertEq(False, bool(obj.isMatch('typedef int SearchTermf;')))
    assertEq(False, bool(obj.isMatch('typedefint SearchTerm;')))
    assertEq(True, bool(obj.isMatch('typedef int SearchTerm;')))
    assertEq(True, bool(obj.isMatch('typedef enum{a,b,c} SearchTerm;')))
    assertEq(True, bool(obj.isMatch('typedef scope::tmplate<enum{a,b,c}, bool, int> SearchTerm;')))
    assertEq(True, bool(obj.isMatch('void SearchTerm()')))
    assertEq(True, bool(obj.isMatch('void SearchTerm<>')))
    assertEq(True, bool(obj.isMatch('template <int a> void SearchTerm()')))
    assertEq(True, bool(obj.isMatch('void Scope::SearchTerm()')))
    assertEq(False, bool(obj.isMatch('SearchTerm(int a)')))
    assertEq(False, bool(obj.isMatch('SearchTerm(int a);')))
    assertEq(False, bool(obj.isMatch('SearchTerm = 4')))
    assertEq(False, bool(obj.isMatch('(void SearchTerm())')))
    assertEq(False, bool(obj.isMatch('go(SearchTerm, other)')))
    assertEq(False, bool(obj.isMatch('go(SearchTerm(), other)')))
    assertEq(False, bool(obj.isMatch('template<SearchTerm, other>')))
    assertEq(False, bool(obj.isMatch('Scope::SearchTerm();'))) # the semicolon kills it
    assertEq(False, bool(obj.isMatch('a.SearchTerm()')))
    assertEq(False, bool(obj.isMatch('a->SearchTerm()')))
    assertEq(False, bool(obj.isMatch('word a.SearchTerm()')))
    assertEq(False, bool(obj.isMatch('word a->SearchTerm()')))
    assertEq(False, bool(obj.isMatch('SearchTerm()')))
    assertEq(False, bool(obj.isMatch('SearchTerm word')))
    assertEq(False, bool(obj.isMatch('SearchTerm word word')))
    assertEq(False, bool(obj.isMatch('//SearchTerm')))
    assertEq(False, bool(obj.isMatch('// SearchTerm')))
    assertEq(False, bool(obj.isMatch('// word SearchTerm()')))
    assertEq(True, bool(obj.isMatch('word SearchTerm')))
    assertEq(True, bool(obj.isMatch('word SearchTerm = ')))
    assertEq(True, bool(obj.isMatch('word SearchTerm = 1234')))
    assertEq(True, bool(obj.isMatch('word SearchTerm = 1234;')))
    assertEq(True, bool(obj.isMatch('word SearchTerm = 1234; // comment')))
    assertEq(True, bool(obj.isMatch('char* SearchTerm()')))
    assertEq(True, bool(obj.isMatch('char * SearchTerm()')))
    assertEq(True, bool(obj.isMatch('char *SearchTerm()')))
    assertEq(True, bool(obj.isMatch('word<int, int> SearchTerm()')))
    assertEq(True, bool(obj.isMatch('word<int, int> SearchTerm(int a=123, bool b)')))
    assertEq(True, bool(obj.isMatch('word<int, int> Scope::SearchTerm()')))
    assertEq(True, bool(obj.isMatch('word<int, int> Scope::SearchTerm(int a=123, bool b)')))
    assertEq(False, bool(obj.isMatch('char* SearchTermF()')))
    assertEq(False, bool(obj.isMatch('char * SearchTermF()')))
    assertEq(False, bool(obj.isMatch('char *SearchTermF()')))
    assertEq(False, bool(obj.isMatch('word SearchTerm;')))
    assertEq(False, bool(obj.isMatch('SearchTerm;')))
    assertEq(False, bool(obj.isMatch('SearchTerm =')))
    assertEq(False, bool(obj.isMatch('= SearchTerm')))
    assertEq(False, bool(obj.isMatch('+ SearchTerm')))
    assertEq(False, bool(obj.isMatch('word = SearchTerm')))
    assertEq(False, bool(obj.isMatch('word + SearchTerm')))
    assertEq(False, bool(obj.isMatch('word , SearchTerm')))
    assertEq(False, bool(obj.isMatch('word, SearchTerm')))
    assertEq(False, bool(obj.isMatch('word; SearchTerm')))
    assertEq(False, bool(obj.isMatch('word.SearchTerm')))
    assertEq(False, bool(obj.isMatch('word->SearchTerm')))
    assertEq(False, bool(obj.isMatch('return SearchTerm')))
    assertEq(False, bool(obj.isMatch('return SearchTerm();')))
    assertEq(False, bool(obj.isMatch('Scope::SearchTerm')))
    assertEq(False, bool(obj.isMatch('Scope::SearchTerm::Other')))
    assertEq(False, bool(obj.isMatch('Scope::SearchTerm Scope::OtherMethod()')))
    assertEq(True, bool(obj.isMatch('typedef char SearchTerm; // comment')))
    assertEq(True, bool(obj.isMatch('typedef unsigned char SearchTerm; // comment')))
    assertEq(True, bool(obj.isMatch('typedef char* SearchTerm;')))
    assertEq(True, bool(obj.isMatch('typedef char * SearchTerm;')))
    assertEq(True, bool(obj.isMatch('typedef char *SearchTerm;')))
    assertEq(True, bool(obj.isMatch('static lua_State* SearchTerm = 0;')))
    assertEq(True, bool(obj.isMatch('static lua_State * SearchTerm = 0;')))
    assertEq(True, bool(obj.isMatch('static lua_State *SearchTerm = 0;')))
    assertEq(True, bool(obj.isMatch('const char* SearchTerm[] = "";')))
    
    obj = FilterLineCDeclaration('SearchTerm')
    assertEq(True, bool(obj.isMatch('int SearchTerm;')))
    assertEq(True, bool(obj.isMatch('int SearchTerm ;')))
    assertEq(True, bool(obj.isMatch('int SearchTerm(int line);')))
    assertEq(True, bool(obj.isMatch('int SearchTerm(int line) ;')))
    assertEq(False, bool(obj.isMatch('SearchTerm(next, buffer, 32);')))
    assertEq(False, bool(obj.isMatch('next = SearchTerm(ps, buffer, 32);')))
    assertEq(False, bool(obj.isMatch('return SearchTerm(ps, buffer, 32);')))
    assertEq(False, bool(obj.isMatch('static char *Scope::SearchTerm(const char *p);')))
    assertEq(True, bool(obj.isMatch('static char *SearchTerm(const char *p);')))
    assertEq(True, bool(obj.isMatch('static Scope::char *SearchTerm(const char *p);')))
    assertEq(False, bool(obj.isMatch('bool Scope::SearchTerm = false;')))
    assertEq(False, bool(obj.isMatch('a = (SearchTerm());')))
    assertEq(False, bool(obj.isMatch('a = SearchTerm;')))
    assertEq(False, bool(obj.isMatch('SearchTerm = a;')))
    assertEq(True, bool(obj.isMatch('bool SearchTerm;')))
    assertEq(True, bool(obj.isMatch('static bool SearchTerm;')))
    assertEq(True, bool(obj.isMatch('extern const SearchTerm[];')))
    
    # examples in scite/src:
    # macros: RTF_SETFONTFACE, GUI_TEXT
    # class: Buffer, Rectangle
    # enum: GrepFlags, IndentationStatus
    # typedef: utf8, WindowID
    # methods: int SciTEBase::IndentOfBlock, int SciTEBase::CallFocused,
    # GetNewExpandString, static const char *GetNextPropItem
    # functions: inline bool isspacechar, static size_t FindCaseInsensitive
    # variables: PropSetFile::caseSensitiveFilenames, static lua_State *luaState,
    # GUI::gui_char propGlobalFileName
    # member vars, for declaration: bool pageStarted. static std::string startupScript
    
if __name__ == '__main__':
    tests()
