# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

class ShowSelectionInfo(object):
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        self.choices = ['S|sum|Sum of numbers',
            'T|stats|Stats e.g. mean of numbers',
            'I|sumtimes|Sum of times (mm:ss)',
            'A|ascii|Show ascii of selected text',
            'C|counting|Line count, word count, char count']
        label = 'Please select some text and choose:'
        ScAskUserChoiceByPressingKey(
            choices=self.choices, label=label, callback=self.onChoiceMade)

    def onChoiceMade(self, choice):
        from scite_extend_ui import ScEditor
        selected = ScEditor.GetSelectedText()
        
        if selected:
            # look for a method named choice
            assert choice in [s.split('|')[1] for s in self.choices]
            method = self.__getattribute__(choice)
            method(selected)
        else:
            print('Nothing is selected.')
    
    def splitLines(self, s):
        s = s.replace('\r\n', '\n')
        s = s.replace('\r', '\n')
        return s.split('\n')
    
    def getFirstNumbers(self, s):
        results = []
        for line in self.splitLines(s):
            if not line.strip():
                continue
            
            firstPartWithoutWhitespace = line.split()[0]
            try:
                results.append(float(firstPartWithoutWhitespace))
            except ValueError:
                print("Skipping line %s which isn't a number." % line)
        
        return results
        
    def sum(self, s):
        nums = self.getFirstNumbers(s)
        print('Sum of %d seen is %f.' % (len(nums), sum(nums)))

    def stats(self, s):
        import operator
        nums = self.getFirstNumbers(s)
        total = sum(nums)
        product = reduce(operator.mul, nums, 1)
        try:
            st = BasicStats()
            mean = st.mean(nums)
            stdev = st.stdev(nums)
            pstdev = st.pstdev(nums)
            print('Sum of %d seen is %f.' % (len(nums), total))
            print('Product is %f' % product)
            print('Mean is %f' % mean)
            print('Sample stddev is %f' % stdev)
            print('Population stddev is %f' % pstdev)
        except ValueError, e:
            print(e)
    
    def sumtimes(self, s):
        totalSeconds = getSumTimes(self.splitLines(s))
        if totalSeconds is not None:
            print('Total seconds: %s' % getFormattedDuration(totalSeconds))
            print('Total seconds: %f' % totalSeconds)
        
    def ascii(self, s):
        print('Ascii values:')
        for c in s:
            show = c if c.isalnum() else ' '
            print('%s \t 0x%02x \t %02d' % (show, ord(c), ord(c)))
    
    def counting(self, s):
        from scite_extend_ui import ScEditor
        chars = len(s)
        wordcount = getWordCount(s)
        lines = len(self.splitLines(s))
        totalLinesInDoc = ScEditor.GetLineCount()
        print('Info about selected text:')
        print('Characters: %d' % chars)
        print('Word count: %d' % wordcount)
        print('Lines selected: %d' % lines)
        print('Total lines in doc: %d' % totalLinesInDoc)
        
        
def lengthOfIterator(it):
    return sum(1 for item in it)

def getWordCount(s):
    import re
    return lengthOfIterator(re.finditer(r'(\S+)', s))

def getSumTimes(lines, silent=False):
    totalSeconds = 0
    for line in lines:
        if not line.strip():
            continue
        
        firstPartWithoutWhitespace = line.split()[0]
        parts = firstPartWithoutWhitespace.split(':')
        if len(parts) != 2:
            print(silent or 'We only support times in the format mm:ss, ' +
                'but got %s' % line)
            return
        
        mm, ss = parts
        totalSeconds += float(mm) * 60 + float(ss)
    return totalSeconds

def getFormattedDuration(seconds):
    if not seconds and seconds != 0:
        return ''
    
    milli = int(seconds * 1000)
    return '%02d:%02d.%03d'%(int(seconds) // 60, int(seconds) % 60, milli % 1000)

class BasicStats(object):
    ''' logic from python's statistics.py '''
    
    def _ss(self, data):
        """Return sum of square deviations of sequence data."""
        c = self.mean(data)
        total = sum((x - c) ** 2 for x in data)
        # The following sum should mathematically equal zero, but due to rounding
        # error may not.
        total2 = sum((x - c) for x in data)
        total -= total2 ** 2 / len(data)
        assert not total < 0, 'negative sum of square deviations: %f' % total
        return total
    
    def mean(self, data):
        n = len(data)
        if n < 1:
            raise ValueError('mean requires at least one data point')
        total = sum(data)
        return total / float(n)
    
    def variance(self, data):
        n = len(data)
        if n < 2:
            raise ValueError('variance requires at least two data points')
        ss = self._ss(data)
        return ss / (float(n) - 1)
    
    def pvariance(self, data, mu=None):
        n = len(data)
        if n < 1:
            raise ValueError('pvariance requires at least one data point')
        ss = self._ss(data)
        return ss / float(n)
    
    def stdev(self, data):
        import math
        return math.sqrt(self.variance(data))
        
    def pstdev(self, data):
        import math
        return math.sqrt(self.pvariance(data))

def DoShowSelectionInfo():
    ShowSelectionInfo().go()

if __name__ == '__main__':
    from ben_python_common import assertEq, assertFloatEq
    
    st = BasicStats()
    assertFloatEq(2.8, st.mean([1, 2, 3, 4, 4]))
    assertFloatEq(1.3720238095238, st.variance([2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5]))
    assertFloatEq(1.25, st.pvariance([0.0, 0.25, 0.25, 1.25, 1.5, 1.75, 2.75, 3.25]))
    assertFloatEq(1.08108741552198, st.stdev([1.5, 2.5, 2.5, 2.75, 3.25, 4.75]))
    assertFloatEq(0.986893273527251, st.pstdev([1.5, 2.5, 2.5, 2.75, 3.25, 4.75]))
    
    assertEq('00:00.000', getFormattedDuration(0))
    assertEq('00:00.001', getFormattedDuration(0.001))
    assertEq('01:01.500', getFormattedDuration(61.5))
    assertEq('06:45.500', getFormattedDuration(6 * 60 + 45.5))
    
    lines = '1:10|2:20|3'.split('|')
    assertEq(None, getSumTimes(lines, silent=' '))
    lines = '1:10|2:20|3:3:3'.split('|')
    assertEq(None, getSumTimes(lines, silent=' '))
    lines = '1:10  |2:40  |3:50  '.split('|')
    assertFloatEq(460, getSumTimes(lines))
    lines = '  1:10  123|  2:40  1:10|  3:50  text'.split('|')
    assertFloatEq(460, getSumTimes(lines))
    
    assertEq(0, getWordCount(''))
    assertEq(1, getWordCount('test'))
    assertEq(15, getWordCount('Lorem ipsum dolor sit amet, consectetur adipiscing ' +
        'elit. In id aliquam lorem, eu pulvinar velit.'))
