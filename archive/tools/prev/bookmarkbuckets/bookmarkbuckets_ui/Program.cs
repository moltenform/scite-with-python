using SHDocVw;
using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace bookmarkbucket_ui
{
    // Removed references to: system.deployment, system.data
    // Added reference to SHDocVw.dll (project->add reference, browse c:\windows\system32\SHDocVw.dll) (Microsoft Internet Controls COM Object)
    // Added reference to Shell32.dll (project->add reference, browse c:\windows\system32\Shell32.dll)
    // Before Application.Run is called, there is no new active window, and so we can determine the current hwnd.

    static class Program
    {
        [STAThread]
        static void Main()
        {
            string[] args = Environment.GetCommandLineArgs();
            if (args.Length > 1)
            {
                string sFirstArg = args[1];
                if (args.Length == 2 && (sFirstArg.ToLowerInvariant().EndsWith(".jpeg") || sFirstArg.ToLowerInvariant().EndsWith(".html")))
                    OnOpenJpeg(new string[] {sFirstArg } );
                else if (args.Length == 2 && sFirstArg.ToLowerInvariant() == "/auto")
                    OnOpenCurrentSelectionInExplorer();
                else
                    MessageBox.Show("Incorrect arguments. Examples:\r\n\r\n bookmarkbucket.exe /auto\r\n bookmarkbucket.exe c:\\test.jpg");
            }
            else
            {
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(new Form1());
            }
        }

        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();

        public static void OnOpenJpeg(string[] files)
        {
            if (files!=null && files.Length>0)
                CallAndCatchExceptions.Call(delegate(object o)
                {
                    new BookmarkBucket().TopOpenWebpagesAssociatedWithJpegs((string[])o);
                }, files);
        }
        public static void OnOpenCurrentSelectionInExplorer()
        {
            IntPtr hwndCurrent = GetForegroundWindow();
            string[] arSelected = getSelectedFileInExplorerWindow(hwndCurrent);
            List<string> listJpegs = new List<string>();

            foreach (string s in arSelected)
                if (s.ToLowerInvariant().EndsWith(".jpeg") || s.ToLowerInvariant().EndsWith(".html"))
                    listJpegs.Add(s);

            OnOpenJpeg(listJpegs.ToArray());
        }

        private static String[] getSelectedFileInExplorerWindow(IntPtr handle)
        {
            List<string> list = new List<string>();
            ShellWindows shellWindows = new SHDocVw.ShellWindows();
            foreach (InternetExplorer window in shellWindows)
            {
                if (window != null && window.HWND==(int)handle && ((Shell32.IShellFolderViewDual2)window.Document) != null)
                {
                    // The .FocusedItem is also available.
                    Shell32.FolderItems items = ((Shell32.IShellFolderViewDual2)window.Document).SelectedItems();
                    if (items != null)
                    {
                        foreach (object o in items)
                        {
                            Shell32.FolderItem item = o as Shell32.FolderItem;
                            if (item != null && item.Path!=null)
                            {
                                list.Add(item.Path);
                            }
                        }
                    }
                }
            }
            return list.ToArray();
        }
        public static string GetExeDirectory()
        {
            string s = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
            if (s == null || s.Length <= 1) throw new Exception("GetExeDirectory failed.");
            return s;
        }
    }
}
