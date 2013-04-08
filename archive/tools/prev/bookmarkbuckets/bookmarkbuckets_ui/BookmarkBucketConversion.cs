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
    public partial class BookmarkBucket
    {
        public void TopRunUnitTests()
        {
            //string sTestDir = @"C:\Users\diamond\Desktop\-frommain\delldev\bookmarkbuckets\bookmarkbuckets_cs\bookmarkbucket\bookmarkbucket_console\bookmarkbucket_ui\test";
            //string s1 = BookmarkBucketCore.GetExifDataSoftware(sTestDir + "\\k.jpeg");
            //string s2 = BookmarkBucketCore.GetExifDataTitle(sTestDir + "\\k.jpeg");
            //string s3 = BookmarkBucketCore.GetExifDataUrl(sTestDir + "\\k.jpeg");
            //MessageBox.Show(String.Format("{0}\n{1}\n{2}\n", s1,s2,s3));

            // convert from old to new.
            //bool b = ThreadPool.SetMaxThreads(4, 4);
            //System.Diagnostics.Debug.Assert(b);

            DialogResult dr = MessageBox.Show("Create new jpgs?", "bb", MessageBoxButtons.YesNo);
            if (dr == DialogResult.No) { ConvertOldToNewWithoutRedownloading(); return; }

            string sDir = InputBoxForm.GetStrInput("All from this directory:", "c:\\example");
            if (sDir == null || !Directory.Exists(sDir)) { MessageBox.Show("Not a valid directory."); return; }

            DirectoryInfo di = new DirectoryInfo(sDir);
            FileInfo[] rgFiles = di.GetFiles("*.jpg");
            foreach (FileInfo fi in rgFiles)
            {
                string sNewname = Path.GetFileNameWithoutExtension(fi.Name.Replace("555 ", "")) + ".png";
                if (File.Exists(sDir + "\\" + sNewname)) throw new BookmarkBucketException("exists png" + fi.Name);
                File.Move(sDir + "\\" + fi.Name, sDir + "\\" + sNewname);
            }

            // make a Model
            BookmarkBucketObjectModel model = new BookmarkBucketObjectModel();
            FileInfo[] rgFilesPng = di.GetFiles("*.png");
            foreach (FileInfo fi in rgFilesPng)
            {
                string sOldUrl = BookmarkBucketCore.GetExifData(fi.FullName, "Comment");
                if (!BookmarkBucketCore.looksLikeAUrl(sOldUrl))
                    throw new BookmarkBucketException("couldnot read url" + fi.Name);

                model.list.Add(new BookmarkBucketItem { sFile = Path.GetFileNameWithoutExtension(fi.Name), sUrl = sOldUrl });
            }

            Form1.g_busy = true;
            Thread oThread = new Thread(delegate()
            {
                CallAndCatchExceptions.Call(delegate(object o)
                {
                    this.ModelToJpegs(model, sDir);
                    Form1.g_busy = false; Form1.g_status = "";
                }, null);
            });
            oThread.Start();
        }
        private void ConvertOldToNewWithoutRedownloading()
        {
            string sDir = InputBoxForm.GetStrInput("All from this directory:", "c:\\example");
            if (sDir == null || !Directory.Exists(sDir)) { MessageBox.Show("Not a valid directory."); return; }

            DirectoryInfo di = new DirectoryInfo(sDir);
            FileInfo[] rgFiles = di.GetFiles("*.jpg");
            foreach (FileInfo fi in rgFiles)
            {
                string sNewname = Path.GetFileNameWithoutExtension(fi.Name.Replace("555 ", "")) + ".png";
                if (File.Exists(sDir + "\\" + sNewname)) throw new BookmarkBucketException("exists png" + fi.Name);
                File.Move(sDir + "\\" + fi.Name, sDir + "\\" + sNewname);
            }

            // set the exifs...
            FileInfo[] rgFilesPng = di.GetFiles("*.png");
            foreach (FileInfo fi in rgFilesPng)
            {
                string sOldUrl = BookmarkBucketCore.GetExifData(fi.FullName, "Comment");
                if (!BookmarkBucketCore.looksLikeAUrl(sOldUrl))
                    throw new BookmarkBucketException("couldnot read url" + fi.Name);

                // convert it to a jpg.
                string sJpeg = sDir + "\\" + Path.GetFileNameWithoutExtension(fi.Name) + ".jpeg";
                using (Bitmap b = new Bitmap(fi.FullName))
                {
                    ImageHelper.BitmapSaveJpegQuality(b, sJpeg, 85);
                }
                if (!File.Exists(sJpeg)) throw new BookmarkBucketException("no jpeg created?");
                File.Delete(fi.FullName);

                BookmarkBucketCore.StripAllExifData(sJpeg);
                BookmarkBucketCore.SetExifData(sJpeg, sOldUrl, Path.GetFileNameWithoutExtension(fi.Name));

                // download the htm!
                string sHtmlName = sDir + "\\" + Path.GetFileNameWithoutExtension(fi.Name) + ".html";
                if (File.Exists(sHtmlName)) throw new BookmarkBucketException("exists html" + fi.Name);
                BookmarkBucketImplementation.DownloadFile(sOldUrl, sHtmlName);
                File.AppendAllText(sHtmlName, strHtmlStamp + sOldUrl + "-->"); // will create file.
            }
        }
    }
}
