using System;
using System.Text;
using System.IO;
using System.Diagnostics;

namespace bookmarkbucket_ui
{
    public static class BookmarkBucketCore
    {
        const string sExifFieldForUrl = "UserComment";
        const string sExifFieldForTitle = "OriginalRawFileName";
        const string sExifFieldForSoftware = "Software";

        
        private static string runAndReadStdOut(string exe, string arguments)
        {
            if (!File.Exists(exe)) throw new BookmarkBucketException("Could not find file "+exe);
            Process p = new Process();
            p.StartInfo.CreateNoWindow = true;
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.FileName = exe;
            p.StartInfo.Arguments = arguments;
            p.Start();
            string output = p.StandardOutput.ReadToEnd(); // Read the output stream first and then wait.
            p.WaitForExit();
            if (p.ExitCode != 0) throw new BookmarkBucketException("Exit code indicates failure for " + exe);
            return output;
        }
        public static void SetExifData(string sFilename, string sUrl, string sTitle)
        {
            if (containsInvalidCharacters(sFilename, true) || containsInvalidCharacters(sUrl, false) || containsInvalidCharacters(sTitle, true))
                throw new BookmarkBucketException("Invalid characters in " + sTitle);
            string sArgs = String.Format("-{0}=\"{1}\" -{2}=\"{3}\" -{4}=\"{5}\" -overwrite_original \"{6}\"", sExifFieldForTitle, sTitle, sExifFieldForUrl, sUrl,
                sExifFieldForSoftware, "halfhourhacks.blogspot.com BookmarkBucket v2", sFilename);
            string sOutput = runAndReadStdOut(Program.GetExeDirectory() + "\\exiftool.exe", sArgs);
            if (!sOutput.Contains("1 image files updated"))
                throw new BookmarkBucketException("Exiftool failed to set " + sTitle + " with result:" + sOutput);
        }

        internal static string GetExifData(string sFilename, string sExifFieldName)
        {
            if (containsInvalidCharacters(sFilename, true) || containsInvalidCharacters(sExifFieldName, false))
                throw new BookmarkBucketException("Invalid characters in " + sFilename);
            string sArgs = String.Format("-S -{0} \"{1}\"", sExifFieldName, sFilename);
            string sOutput = runAndReadStdOut(Program.GetExeDirectory() + ".\\exiftool.exe", sArgs);
            sOutput = sOutput.Trim();
            string sExpectStart = sExifFieldName + ": ";
            if (!sOutput.StartsWith(sExpectStart))
                throw new BookmarkBucketException("Was this file created by BookmarkBuckets? Exiftool failed to get " + Path.GetFileName(sFilename) + " with result:" + sOutput);
            else
                return sOutput.Substring(sExpectStart.Length);
        }
        public static string GetExifDataUrl(string sFilename) { return GetExifData(sFilename, sExifFieldForUrl); }
        public static string GetExifDataTitle(string sFilename) { return GetExifData(sFilename, sExifFieldForTitle); }
        public static string GetExifDataSoftware(string sFilename) { return GetExifData(sFilename, sExifFieldForSoftware); }

        internal static void StripAllExifData(string sFilename)
        {
            if (containsInvalidCharacters(sFilename, true))
                throw new BookmarkBucketException("Invalid characters in " + sFilename);
            string sArgs = String.Format("-all= -overwrite_original \"{0}\"", sFilename);
            string sOutput = runAndReadStdOut(Program.GetExeDirectory() + "\\exiftool.exe", sArgs);
        }

        public static void LaunchWebpage(string sUrl)
        {
            if (!looksLikeAUrl(sUrl))
                throw new BookmarkBucketException("invalid url");
            System.Diagnostics.ProcessStartInfo info = new System.Diagnostics.ProcessStartInfo("\"" + sUrl + "\"");
            info.UseShellExecute = true; // necessary. the no-quotes and no-space requirements should make this ok.
            info.Verb = "open";
            System.Diagnostics.Process.Start(info);
        }
        public static bool looksLikeAUrl(string s)
        {
            return (s!=null && (s.StartsWith("http://") || s.StartsWith("https://")) && !containsInvalidCharacters(s, false) && !s.Contains("\\"));
        }
        public static bool containsInvalidCharacters(string s, bool bSpacesAllowed)
        {
            return s.Contains("\"") || s.Contains("|") || s.Contains("\r") || s.Contains("\n") || (!bSpacesAllowed && s.Contains(" "));
        }
    }

    public class BookmarkBucketException : System.Exception
    {
        private Exception m_innerException;
        private string m_string;
        public BookmarkBucketException(string message)
        {
            this.m_string = message;
        }
        public BookmarkBucketException(string message, Exception inner)
        {
            this.m_string = message;
            this.m_innerException = inner;
        }
        public override string ToString()
        {
            return "BookmarkBucket: " + m_string + "\n" + ((m_innerException != null) ? m_innerException.ToString() : "");
        }
    }
}

