
Simplistic Source Indexing Processor
Ben Fisher, 2011. Released under the GPLv3 license.

This program processes source code and generates an index of terms that were used in the file. After the index is built, searches can be run very quickly, even on a large codebase. It is intended for c and c++ code, but has partial support for other languages like java and c#. It only supports an index for whole-string matching.

<h2>Usage</h2>
First, make a copy of ssipexample.cfg and name it ssip.cfg. Edit the file so that it points to a directory containing source code.
[main]  srcdir1=C:\path\to\my\source

Then, from a command line, one can do the following:
Type sssip –s main, and you should see a result for your main() function.
Full options are:
<pre>
sssip -s word		Search for a word
sssip -start		Re-build index
sssip -noindex word		Search for a word without using index
sssip -noindexnowhole word		Search for a partial word without using index
</pre>

If you update one of your source files, the index will notice the change and keep itself up to date.

This program is designed for speed, so it should be able to make a complete index quickly.

<h2>Implementation</h2>

I use IDEs like Eclipse and Visual Studio for debugging, but find them far too bulky for everyday programming. They are slow to open and less customizable than my code editor of choice, SciTE. However, IDEs do have some useful features, in particular Go to Definition (which takes the currently-selected symbol and opens the file and line on which it is defined). SSIP is my first step in adding features like this to code editors like SciTE.

My primary goal is speed. I want this to be usable on large codebases. I want even the initial run, creating the index from scratch, to take less than 10 seconds. Otherwise, there’s no point in generating an index, as a full-file search would be sufficient. I also found it enjoyable to optimize and tune a program, eschewing all C++ features (classes, exceptions) in favor of fast, raw, procedural code.

I struck upon a way to quickly create an index that actually does not store any text at all. I used what is known as a hash function to map every word into a number. The function always maps the same word to the same number. For example, the word ‘hello’ maps to the number 1634674. The word ‘hello2’, though, maps to a completely different number, 26453545. When the user searches for the term ‘hello’, I use the same hash function to find its corresponding number and search only for the number.
This may seem too good to be true: I’ve transformed the 6 byte string ‘hello2’ into a 4 byte integer. The catch is that several inputs can map to the same number.  ‘zsesdvf’, ‘rtyrqtrdg’, and ‘hello2’ could all map to the same number, 26453545. This is perfectly fine for my search index, though, because before displaying the results to the user, I’ll do a second check to make sure that the result matches what the user typed. In other words, this type of search could return false positives, but the false positives can be easily filtered out, and in the end the results are always correct.

A drawback of this method is that only full words can be searched.

The initial search creates a database from scratch. The name of each file encountered is also stored along with its last-modified time. Subsequent searches will traverse through the files again and check each file’s last-modified time. If the file is new, or its update time is more recent than what we have, we process the file and update the database.
 
<h2>More Implementation Details</h2>
I chose to use Sqlite to store data. By using prepared queries, the sql only had to be parsed once per session, leading to performance improvements. 

I also adjusted the hash function so that it didn’t require the length of the string up front. This allowed me to stream each character into the hash, and avoid any second buffer of the current word. (In general, I’ve noticed that avoiding memory allocations and having fewer buffers can lead to significant gains in performance).

At first, I wrote a threadpool system where a main thread would hand out files to be processed by the workers. This worked, but I was surprised to see that the number of worker threads barely affected the speed of execution. Unfortunately, writing to the database was significantly slower than reading from the text file, and since sqlite only allows one writer at a time, this was a clear bottleneck. It would have been possible to create separate databases to be later merged, but this was too much of a hack even for me. I returned to single threaded execution, which did simplify the code.

At this point, the program was logging string hash, line number found, id, file id, and other flags for each word. Because the id was incrementing, I could search for two consecutive terms with a bit of sql. The other flags included whether the line was indented or not, and the surrounding characters. Surrounding characters could among other things distinguish a method implementation, like ::foo. The size of the database on disk was rather large, though.

Because writing to the database was my bottleneck, if I could store less data, the program would be faster.

I realized that my prior experience showed me that reading through a file was unexpectedly fast. So, I decided to not even store the line number in my index at all. Results saying ‘the string “hello” is somewhere in the file “foo.cpp”’ is good enough, because it takes hardly any time to run through foo.cpp to list the true results.

This also meant that I only had to record a particular string once per file. I came up with a very effective trick to rapidly detect duplicates. I was already hashing each string to a number. I reduced the number of bits in the hash to 24, probably reasonable because most words in source code are short. (Remember that in my design collisions might cause false positives that take time to be filtered out, but won’t affect correctness). This means that the number of distinct strings I was tracking was 2 to the 24th power, or 16,777,216. I then allocated a chunk of memory, 16,777,216 bytes worth to be exact. For each file I cleared all of the memory to 0, and as each string appeared I would find its hash and ‘check off’ the corresponding place in memory. I could then quickly see if a string had already been encountered in a file. (I could have also done this at the bit level, but bit operations take time, and a 24-bit hash has been sufficient). One might worry that hash collisions could cause us to incorrectly skip over a word because its brother has already been added to the db for that file, but this is not the case, because I consistently use the same hash algorithm. When searching, the program must still look through the file, because that hash did occur in that file. 

The next step is for me to write a Python wrapper around Ssip that lets me ask questions like ‘find the constructor of the CFoo class’, ‘find the implementation of the bar() method’, and ‘find the type of the baz global variable’. I’ll then plug this into my code editor and be well on my way to having my own lightweight productivity toolkit.

<h2>Cfg file options</h2>
Add verbose=1 to display a bit more information.
If you run into the max directory depth limit, this can be adjusted with
maxdirdepth=20
and so on.

