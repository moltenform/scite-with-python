using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading;
using System.Windows.Forms;

// Dependencies:
// CutyCapt.exe
// CutyCapt-Win32-2010-04-26
// http://cutycapt.sourceforge.net/
// sha1 457dbb432842f2d9d82a3d417b6b3513a265d800
// 
// exiftool.exe
// exiftool-9.10
// http://www.sno.phy.queensu.ca/~phil/exiftool/
// a9ab76cef954316c14b622842fa3d4f608c72451

namespace bookmarkbucket_ui
{
    public partial class Form1 : Form
    {
        public static string g_status; public static bool g_busy;
        public Form1()
        {
            InitializeComponent();
            this.AllowDrop = true;
            g_status = "";
            g_busy = false;
        }

        private void createFromURLShortcutsToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string sDir = InputBoxForm.GetStrInput("All URL shortcuts from this directory:", "c:\\example");
            if (sDir == null || !Directory.Exists(sDir)) { MessageBox.Show("Not a valid directory."); return; }
            
            // create bg thread.
            g_busy = true; this.btn1.Enabled = false;
            Thread oThread = new Thread(delegate()
            {
                CallAndCatchExceptions.Call(delegate(object param)
                {
                    new BookmarkBucket().TopUrlShortcutsToJpegs((string) param);
                }, sDir);
                g_busy = false; g_status = "";
            });
            oThread.Start();
        }
        private void createFromXmlFileToolStripMenuItem_Click(object sender, EventArgs e)
        {
            CallAndCatchExceptions.Call(delegate(object o) { new BookmarkBucket().TopXmlFileToUrlShortcuts(); }, null);
        }
        private void exportToCSVToolStripMenuItem_Click(object sender, EventArgs e)
        {
            CallAndCatchExceptions.Call(delegate(object o) { new BookmarkBucket().TopJpegsToXmlFile(); }, null);
        }
        private void exportToURLShortcutsToolStripMenuItem_Click(object sender, EventArgs e)
        {
            CallAndCatchExceptions.Call(delegate(object o) { new BookmarkBucket().TopJpegsToUrlShortcuts(); }, null);
        }
        
        
        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            this.Close();
        }
        private void websiteToolStripMenuItem_Click(object sender, EventArgs e)
        {
            BookmarkBucketCore.LaunchWebpage("http://halfhourhacks.blogspot.com/");
        }
        private void aboutToolStripMenuItem_Click(object sender, EventArgs e)
        {
            MessageBox.Show("BookmarkBucket v2, by Ben Fisher 2011\nUses CutyCapt by Bjorn Hohrmann.\nUses ExifTool by Phil Harvey.\nGPL v3\n\nhttp://halfhourhacks.blogspot.com");
        }


        private void btn1_Click(object sender, EventArgs e)
        {
            if ((ModifierKeys & Keys.Shift) == Keys.Shift)
                CallAndCatchExceptions.Call(delegate(object o) { new BookmarkBucket().TopRunUnitTests(); }, null);
            else
                createFromURLShortcutsToolStripMenuItem_Click(null, null);
        }

        private void timerUpdateStatus_Tick(object sender, EventArgs e)
        {
            this.lblStatus.Text = g_status;
            this.btn1.Enabled = !g_busy;
        }

        private void autoOpenToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string s = "How to set up auto-open:\r\n\r\n 1) Download a free/open source hotkey-launcher like Clavier+. \r\n 2) Create a hotkey to start 'c:\\path\\to\\bookmarkbucket.exe /auto' \r\n 3) In Windows Explorer, select some .jpeg files and press the hotkey. \r\n 4) The corresponding webpages will open in your default browser!";
            s += "\r\n\r\n(Associating .jpeg files with bookmarkbucket.exe will also work, but this is less convenient. Right-click and 'open with' from Explorer should work too. All of this is only supported in Win7 but may work in other versions.)";
            MessageBox.Show(s);
        }

        private void Form1_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
                e.Effect = DragDropEffects.Copy;
        }
        private void Form1_DragDrop(object sender, DragEventArgs e)
        {
            string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
            if ((ModifierKeys & Keys.Shift) == Keys.Shift)
            {
                if (files.Length > 1) MessageBox.Show("Warning: only processing first one");
                CallAndCatchExceptions.Call(delegate(object o)
                {
                    new BookmarkBucket().TopCreateManualShortcut((string)o);
                },
                   files[0]);
            }
            else
            {
                CallAndCatchExceptions.Call(delegate(object o)
                {
                    new BookmarkBucket().TopOpenWebpagesAssociatedWithJpegs((string[])o);
                },
                    files);
            }
        }

        private void createOneShortcutToolStripMenuItem_Click(object sender, EventArgs e)
        {
            CallAndCatchExceptions.Call(delegate(object o) { new BookmarkBucket().TopCreateOneShortcut(false); }, null);
        }

        private void jpegIntoShortcutToolStripMenuItem_Click(object sender, EventArgs e)
        {
            CallAndCatchExceptions.Call(delegate(object o) { new BookmarkBucket().TopCreateOneShortcut(true); }, null);
        }
    }

    public static class CallAndCatchExceptions
    {
        public delegate void BookmarkBucketOperation(object o);
        public static void Call(BookmarkBucketOperation b, object param)
        {
            // Simply runs code, catches exceptions, and displays a messagebox.
            try
            {
                b(param);
            }
            catch (Exception e)
            {
                System.Diagnostics.Debug.Assert(false);
                string s = e.ToString().Replace("Exception", "").Replace("exception", "");
                MessageBox.Show(s);
            }
        }
    }
}
