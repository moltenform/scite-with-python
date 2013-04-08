using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Drawing;
using System.Windows.Forms;
using System.Net;
using System.Xml.Serialization;
using System.Threading;

namespace bookmarkbucket_ui
{
    public class BookmarkBucketItem
    {
        public string sFile; public string sUrl;
        public BookmarkBucketItem() { sFile = sUrl = ""; }
        public string GetNameWithoutExtension()
        {
            string sExt = Path.GetExtension(sFile).ToLowerInvariant();
            if (sExt == ".url" || sExt==".jpg" || sExt==".jpeg")
                return Path.GetFileNameWithoutExtension(sFile);
            else
                return sFile;
        }
    }

    public class BookmarkBucketObjectModel
    {
        public int version;
        public List<BookmarkBucketItem> list;
        public BookmarkBucketObjectModel() { list = new List<BookmarkBucketItem>(); version = 2; }
    }

    public partial class BookmarkBucket
    {
        private const string strHtmlStamp = "<!-- Bookmarkbuckets, from ";
#region TopLevel
        public void TopUrlShortcutsToJpegs(string sDir)
        {
            if (sDir==null) return;
            BookmarkBucketObjectModel obj = UrlShortcutsToModel(sDir);
            ModelToJpegs(obj, sDir);
            if (obj.list.Count == 0) MessageBox.Show("None seen.");
            Form1.g_status = "";
        }
        public void TopJpegsToXmlFile()
        {
            BookmarkBucketObjectModel obj = JpegFilesToModelAskDirectory();
            if (obj == null) return;
            string sFilename = ImageHelper.GetSaveString("xml", "Save xml file");
            if (sFilename == null) return;
            ModelToXmlFile(obj, sFilename);
        }
        public void TopJpegsToUrlShortcuts()
        {
            BookmarkBucketObjectModel obj = JpegFilesToModelAskDirectory();
            if (obj == null) return;
            string sFilename = ImageHelper.GetSaveString("url", "Save many URL shortcuts into this location:");
            if (sFilename == null) return;
            ModelToUrlShortcuts(obj, Path.GetDirectoryName(sFilename));
        }
        public void TopXmlFileToUrlShortcuts()
        {
            string sFilename = ImageHelper.GetOpenString("xml", "Select xml file:");
            if (sFilename == null) return;

            BookmarkBucketObjectModel obj = XmlFileToModel(sFilename);
            if (obj == null) return;
            string sOutFilename = ImageHelper.GetSaveString("url", "Save many URL shortcuts into this location:");
            if (sOutFilename == null) return;
            ModelToUrlShortcuts(obj, Path.GetDirectoryName(sOutFilename));
        }
 #endregion

#region ModelToJpegs
        private void ModelItemToJpeg(BookmarkBucketItem item, string sDir)
        {
            // If the webpage cannot be loaded, we want to create a .html and .jpeg anyways.
            // 1) save html
            string sHtml = sDir + "\\" + item.GetNameWithoutExtension() + ".html";
            bool bGotHtml = BookmarkBucketImplementation.DownloadFile(item.sUrl, sHtml);
            File.AppendAllText(sHtml, strHtmlStamp + item.sUrl + "-->"); // will create file.

            // 2) save png screenshot
            string sPng = sDir + "\\" + item.GetNameWithoutExtension() + ".png";
            bool bSucceeded = BookmarkBucketImplementation.DownloadWebsiteSnapshot(item.sUrl, sPng);
            if (!bSucceeded) { using (Bitmap b = ImageHelper.GetBlankBitmap(300, 300)) { b.Save(sPng); } }

            // 3) resize and convert png to jpeg
            string sJpeg = sDir + "\\" + item.GetNameWithoutExtension() + ".jpeg";
            ImageHelper.ResizeAndTruncateAndSaveImage(sPng, sJpeg, 400, 300, 0.5f, 84, false);
            File.Delete(sPng);
            if (!File.Exists(sJpeg)) throw new BookmarkBucketException("Jpeg file expected to be created for '" + item.sFile + "', but was not found");

            // 4) write exif info to jpeg
            BookmarkBucketCore.SetExifData(sJpeg, item.sUrl, item.GetNameWithoutExtension());
        }
        class ModelToJpegsParameters { public object locker; public BookmarkBucketObjectModel model; public int iItemLatest; public string sDir; }
        private void ModelToJpegsThread(object objparam)
        {
            ModelToJpegsParameters param = objparam as ModelToJpegsParameters;
            try
            {
                while (true)
                {
                    if (param.model.version == -1) // someone told us to stop.
                        return;

                    int nWhichToProcess = -1;
                    lock (param.locker)
                    {
                        nWhichToProcess = param.iItemLatest;
                        param.iItemLatest++;
                        if (nWhichToProcess < param.model.list.Count)
                            Form1.g_status = "Downloading " + (nWhichToProcess + 1) + " of " + param.model.list.Count + "...";
                        else
                            return;
                    }

                    ModelItemToJpeg(param.model.list[nWhichToProcess], param.sDir);
                }
            }
            catch (Exception e)
            {
                param.model.version = -1; // tell everyone else to stop.
                string s = e.ToString().Replace("Exception", "").Replace("exception", "");
                System.Diagnostics.Debug.Assert(false);
                MessageBox.Show(s);
            }
        }
        private void ModelToJpegs(BookmarkBucketObjectModel obj, string sDir)
        {
            if (obj == null || obj.list.Count == 0) return;
            sDir += "\\out";
            if (Directory.Exists(sDir)) throw new BookmarkBucketException("'out' directory already exists.");
            Directory.CreateDirectory(sDir);

            // first, make sure we won't overwrite files.
            foreach (BookmarkBucketItem item in obj.list)
            {
                if (item.sFile.Length == 0 || item.sUrl.Length == 0)
                    throw new BookmarkBucketException("Missing url or title.");
                if (!BookmarkBucketCore.looksLikeAUrl(item.sUrl))
                    throw new BookmarkBucketException("invalid url");
                if (File.Exists(sDir + "\\" + item.GetNameWithoutExtension() + ".jpeg"))
                    throw new BookmarkBucketException("Jpeg for '" + item.GetNameWithoutExtension() + "' already exists.");
                if (File.Exists(sDir + "\\" + item.GetNameWithoutExtension() + ".png"))
                    throw new BookmarkBucketException("Png for '" + item.GetNameWithoutExtension() + "' already exists.");
                if (File.Exists(sDir + "\\" + item.GetNameWithoutExtension() + ".html"))
                    throw new BookmarkBucketException("Html for '" + item.GetNameWithoutExtension() + "' already exists.");
            }
            // test write access.
            try { File.WriteAllText(sDir + "\\!!temp!!.test", "test"); }
            catch (IOException) { throw new BookmarkBucketException("Apparently no write access here..."); }
            finally { if (File.Exists(sDir + "\\!!temp!!.test")) File.Delete(sDir + "\\!!temp!!.test"); }

            // use my own threadpool instead of c#'s because I want to limit number of threads running.
            int nThreads = 4;
            ModelToJpegsParameters param = new ModelToJpegsParameters { iItemLatest = 0, locker = new object(), model = obj, sDir = sDir };
            Thread[] threads = new Thread[nThreads];
            for (int i = 0; i < nThreads; i++)
            {
                threads[i] = new Thread(new ParameterizedThreadStart(this.ModelToJpegsThread));
                threads[i].Start(param);
            }
            // wait for all threads to complete. note that obj.version will be negative if an error occurred.
            for (int i = 0; i < nThreads; i++)
                threads[i].Join();
        }
#endregion

        private BookmarkBucketObjectModel JpegFilesToModel(string sDir)
        {
            if (!Directory.Exists(sDir)) throw new BookmarkBucketException("Dir does not exist");
            BookmarkBucketObjectModel model = new BookmarkBucketObjectModel();
            DirectoryInfo di = new DirectoryInfo(sDir);
            FileInfo[] rgFiles = di.GetFiles("*.JPEG");
            foreach (FileInfo fi in rgFiles)
            {
                string sUrl = BookmarkBucketCore.GetExifDataUrl(sDir + "\\" + fi.Name);
                if (sUrl == null || sUrl.Length == 0) throw new BookmarkBucketException("Url is null in " + fi.Name);
                
                model.list.Add(new BookmarkBucketItem { sFile = Path.GetFileNameWithoutExtension(fi.Name), sUrl = sUrl });
            }
            return model;
        }
        private BookmarkBucketObjectModel JpegFilesToModelAskDirectory()
        {
            string sInputDir = ImageHelper.GetOpenString("jpeg", "Select BookmarkBucket jpegs in this directory:");
            if (sInputDir == null) return null;
            BookmarkBucketObjectModel obj = JpegFilesToModel(Path.GetDirectoryName(sInputDir));
            if (obj.list.Count == 0) { MessageBox.Show("None seen."); return null; }
            return obj;
        }

        private void ModelToXmlFile(BookmarkBucketObjectModel obj, string sFilename)
        {
            XmlSerializer xmlS = new XmlSerializer(typeof(BookmarkBucketObjectModel));
            using (TextWriter writeFileStream = new StreamWriter(sFilename))
            {
                xmlS.Serialize(writeFileStream, obj);
            }
        }
        private BookmarkBucketObjectModel XmlFileToModel(string sFilename)
        {
            XmlSerializer xmlS = new XmlSerializer(typeof(BookmarkBucketObjectModel));
            BookmarkBucketObjectModel newDocument;

            try
            {
                using (TextReader readFileStream = new StreamReader(sFilename))
                    newDocument = xmlS.Deserialize(readFileStream) as BookmarkBucketObjectModel;
            }
            catch (InvalidOperationException)
            {
                MessageBox.Show("This xml file doesn't appear to belong to BookmarkBucket. Make sure this is an xml file saved by the current version of BookmarkBucket.");
                return null;
            }
            return newDocument;
        }
        

        private void ModelToUrlShortcuts(BookmarkBucketObjectModel obj, string sDir)
        {
            // make sure filenames don't exist
            if (obj == null || obj.list.Count == 0) return;
            if (sDir==null||!Directory.Exists(sDir)) throw new BookmarkBucketException("Output directory does not exist"); 

            // first, make sure we won't overwrite files.
            foreach (BookmarkBucketItem item in obj.list)
            {
                if (item.sFile.Length == 0 || item.sUrl.Length == 0)
                    throw new BookmarkBucketException("Missing url or title.");
                if (File.Exists(sDir + "\\" + item.GetNameWithoutExtension() + ".url"))
                    throw new BookmarkBucketException("Url shortcut for '" + item.GetNameWithoutExtension() + "' already exists.");
            }

            // write the url shortcuts (we'll throw if access denied)
            foreach (BookmarkBucketItem item in obj.list)
            {
                ModelItemToUrlShortcut(sDir + "\\" + item.GetNameWithoutExtension() + ".url", item.GetNameWithoutExtension(), item.sUrl);
            }
        }
        private void ModelItemToUrlShortcut(string sFilename, string sTitle, string sUrl)
        {
            string sOut = "[InternetShortcut]\r\nURL=";
            sOut += sUrl + "\r\n"; // note closing newline
            File.WriteAllText(sFilename, sOut);
        }
        private BookmarkBucketItem UrlShortcutToModelItem(string strFullfilename, string sName)
        {
            BookmarkBucketItem item = new BookmarkBucketItem { sUrl = "", sFile = sName };
            string sTxt = File.ReadAllText(strFullfilename);
            sTxt = sTxt.Replace("\r\n", "\n");
            string[] astr = sTxt.Split(new char[] { '\n' });
            foreach (string s in astr)
            {
                if (s.StartsWith("URL="))
                    item.sUrl = s.Substring("URL=".Length);
            }
            if (item.sUrl.Length == 0) throw new BookmarkBucketException("Could not find url in file " + sName + ".");
            return item;
        }
        private BookmarkBucketObjectModel UrlShortcutsToModel(string sDir)
        {
            if (!Directory.Exists(sDir)) throw new BookmarkBucketException("Dir does not exist");
            BookmarkBucketObjectModel model = new BookmarkBucketObjectModel();
            DirectoryInfo di = new DirectoryInfo(sDir);
            FileInfo[] rgFiles = di.GetFiles("*.URL");
            foreach (FileInfo fi in rgFiles)
            {
                model.list.Add(UrlShortcutToModelItem(sDir + "\\" + fi.Name, fi.Name));
            }
            return model;
        }

        public void TopOpenWebpagesAssociatedWithJpegs(string[] files)
        {
            if (files == null || files.Length == 0) return;
            foreach (string file in files)
            {
                if (file.ToLowerInvariant().EndsWith(".jpeg"))
                {
                    string sUrl = BookmarkBucketCore.GetExifDataUrl(file);
                    if (sUrl == null || sUrl.Length == 0)
                    { MessageBox.Show("Url does not appear to be valid."); return; }
                    BookmarkBucketCore.LaunchWebpage(sUrl);
                }
                else if (file.ToLowerInvariant().EndsWith(".html"))
                {
                    string sAll = File.ReadAllText(file);
                    int index = sAll.IndexOf(strHtmlStamp, StringComparison.InvariantCulture);
                    if (index != -1)
                    {
                        string strRest = sAll.Substring(index + strHtmlStamp.Length).Trim().Replace("-->", "");
                        if (BookmarkBucketCore.looksLikeAUrl(strRest) && !strRest.Contains("<") && !strRest.Contains(">") && strRest.Length<200)
                            BookmarkBucketCore.LaunchWebpage(strRest);
                    }
                    sAll = null;
                }
                else
                {
                    MessageBox.Show("Please use only .jpeg files, as created by BookmarkBucket."); return;
                }
            }
        }
        
        public void TopCreateOneShortcut(bool bJpegAlreadyExists)
        {
            string sUrl = InputBoxForm.GetStrInput("Enter URL:", "http://example");
            if (!BookmarkBucketCore.looksLikeAUrl(sUrl)) return;

            if (bJpegAlreadyExists)
            {
                string sInputJpeg = ImageHelper.GetOpenString("jpeg", "Select a jpeg:");
                if (sInputJpeg == null || !File.Exists(sInputJpeg)) return;
                BookmarkBucketCore.StripAllExifData(sInputJpeg);
                BookmarkBucketCore.SetExifData(sInputJpeg, sUrl, Path.GetFileNameWithoutExtension(sInputJpeg));
            }
            else
            {
                string sOutJpeg = ImageHelper.GetSaveString("jpeg", "Save jpeg to:");
                if (sOutJpeg == null) return;
                string sDir = Path.GetDirectoryName(sOutJpeg);
                BookmarkBucketItem item = new BookmarkBucketItem { sFile = Path.GetFileNameWithoutExtension(sOutJpeg), sUrl = sUrl};
                ModelItemToJpeg(item, sDir);
            }
            
        }

        public void TopCreateManualShortcut(string sFilename)
        {
            string sUrl = InputBoxForm.GetStrInput("Stamp URL on a file - Enter URL:", "http://example");
            if (!BookmarkBucketCore.looksLikeAUrl(sUrl)) return;
            if (sFilename.ToLowerInvariant().EndsWith(".html"))
            {
                File.AppendAllText(sFilename, strHtmlStamp + sUrl + "-->");
            }
            else if (sFilename.ToLowerInvariant().EndsWith(".jpeg"))
            {
                BookmarkBucketCore.StripAllExifData(sFilename);
                BookmarkBucketCore.SetExifData(sFilename, sUrl, Path.GetFileNameWithoutExtension(sFilename));
            }
            else
            {
                MessageBox.Show("Try a .html or .jpeg file");
            }
        }
    }


    internal static class BookmarkBucketImplementation
    {
        public static bool DownloadFile(string sUrl, string sDest)
        {
            try
            {
                using (WebClient client = new WebClient())
                {
                    client.DownloadFile(sUrl, sDest);
                }
            }
            catch (System.Net.WebException) { return false; }
            catch (System.NotImplementedException) { return false; }
            return File.Exists(sDest);
        }
        public static bool DownloadWebsiteSnapshot(string sUrl, string sDest)
        {
            if (!BookmarkBucketCore.looksLikeAUrl(sUrl))
                throw new BookmarkBucketException("invalid url");
            string sOptions = " \"--url=" + sUrl + "\"";
            sOptions += " \"--out=" + sDest + "\"";
            sOptions += " --max-wait=40000 --delay=1000 --java=off --plugins=off";
            System.Diagnostics.ProcessStartInfo info = new System.Diagnostics.ProcessStartInfo();
            //Environment.
            info.FileName = Program.GetExeDirectory()+"\\CutyCapt.exe";
            if (!File.Exists(info.FileName))
                throw new BookmarkBucketException("Cannot find " + info.FileName);
            info.Arguments = sOptions;
            info.UseShellExecute = false;
            info.Verb = "open";
            info.CreateNoWindow = true;
            System.Diagnostics.Process p = System.Diagnostics.Process.Start(info);
            p.WaitForExit(45 * 1000);
            return File.Exists(sDest);
        }

       
    }
    
}
