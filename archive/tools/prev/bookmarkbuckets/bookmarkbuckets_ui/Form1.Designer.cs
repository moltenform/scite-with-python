namespace bookmarkbucket_ui
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.fileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.createFromURLShortcutsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripMenuItem1 = new System.Windows.Forms.ToolStripSeparator();
            this.exitToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.toolsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportToXmlToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportToURLShortcutsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.createFromXmlFileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripMenuItem2 = new System.Windows.Forms.ToolStripSeparator();
            this.createOneShortcutToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripMenuItem3 = new System.Windows.Forms.ToolStripSeparator();
            this.autoOpenToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.helpToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.aboutToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.websiteToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.btn1 = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.lblStatus = new System.Windows.Forms.Label();
            this.timerUpdateStatus = new System.Windows.Forms.Timer(this.components);
            this.jpegIntoShortcutToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.fileToolStripMenuItem,
            this.toolsToolStripMenuItem,
            this.helpToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(310, 24);
            this.menuStrip1.TabIndex = 0;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // fileToolStripMenuItem
            // 
            this.fileToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.createFromURLShortcutsToolStripMenuItem,
            this.toolStripMenuItem1,
            this.exitToolStripMenuItem});
            this.fileToolStripMenuItem.Name = "fileToolStripMenuItem";
            this.fileToolStripMenuItem.Size = new System.Drawing.Size(37, 20);
            this.fileToolStripMenuItem.Text = "&File";
            // 
            // createFromURLShortcutsToolStripMenuItem
            // 
            this.createFromURLShortcutsToolStripMenuItem.Name = "createFromURLShortcutsToolStripMenuItem";
            this.createFromURLShortcutsToolStripMenuItem.Size = new System.Drawing.Size(322, 22);
            this.createFromURLShortcutsToolStripMenuItem.Text = "Transform &URL shortcuts into JPEG screenshots";
            this.createFromURLShortcutsToolStripMenuItem.Click += new System.EventHandler(this.createFromURLShortcutsToolStripMenuItem_Click);
            // 
            // toolStripMenuItem1
            // 
            this.toolStripMenuItem1.Name = "toolStripMenuItem1";
            this.toolStripMenuItem1.Size = new System.Drawing.Size(319, 6);
            // 
            // exitToolStripMenuItem
            // 
            this.exitToolStripMenuItem.Name = "exitToolStripMenuItem";
            this.exitToolStripMenuItem.Size = new System.Drawing.Size(322, 22);
            this.exitToolStripMenuItem.Text = "E&xit";
            this.exitToolStripMenuItem.Click += new System.EventHandler(this.exitToolStripMenuItem_Click);
            // 
            // toolsToolStripMenuItem
            // 
            this.toolsToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.exportToXmlToolStripMenuItem,
            this.exportToURLShortcutsToolStripMenuItem,
            this.createFromXmlFileToolStripMenuItem,
            this.toolStripMenuItem2,
            this.createOneShortcutToolStripMenuItem,
            this.jpegIntoShortcutToolStripMenuItem,
            this.toolStripMenuItem3,
            this.autoOpenToolStripMenuItem});
            this.toolsToolStripMenuItem.Name = "toolsToolStripMenuItem";
            this.toolsToolStripMenuItem.Size = new System.Drawing.Size(48, 20);
            this.toolsToolStripMenuItem.Text = "&Tools";
            // 
            // exportToXmlToolStripMenuItem
            // 
            this.exportToXmlToolStripMenuItem.Name = "exportToXmlToolStripMenuItem";
            this.exportToXmlToolStripMenuItem.Size = new System.Drawing.Size(243, 22);
            this.exportToXmlToolStripMenuItem.Text = "&Export JPEGs to XML file";
            this.exportToXmlToolStripMenuItem.Click += new System.EventHandler(this.exportToCSVToolStripMenuItem_Click);
            // 
            // exportToURLShortcutsToolStripMenuItem
            // 
            this.exportToURLShortcutsToolStripMenuItem.Name = "exportToURLShortcutsToolStripMenuItem";
            this.exportToURLShortcutsToolStripMenuItem.Size = new System.Drawing.Size(243, 22);
            this.exportToURLShortcutsToolStripMenuItem.Text = "Export JPEGs to &URL shortcuts";
            this.exportToURLShortcutsToolStripMenuItem.Click += new System.EventHandler(this.exportToURLShortcutsToolStripMenuItem_Click);
            // 
            // createFromXmlFileToolStripMenuItem
            // 
            this.createFromXmlFileToolStripMenuItem.Name = "createFromXmlFileToolStripMenuItem";
            this.createFromXmlFileToolStripMenuItem.Size = new System.Drawing.Size(243, 22);
            this.createFromXmlFileToolStripMenuItem.Text = "Export &XML file to URL shortcuts";
            this.createFromXmlFileToolStripMenuItem.Click += new System.EventHandler(this.createFromXmlFileToolStripMenuItem_Click);
            // 
            // toolStripMenuItem2
            // 
            this.toolStripMenuItem2.Name = "toolStripMenuItem2";
            this.toolStripMenuItem2.Size = new System.Drawing.Size(240, 6);
            // 
            // createOneShortcutToolStripMenuItem
            // 
            this.createOneShortcutToolStripMenuItem.Name = "createOneShortcutToolStripMenuItem";
            this.createOneShortcutToolStripMenuItem.Size = new System.Drawing.Size(243, 22);
            this.createOneShortcutToolStripMenuItem.Text = "&Create one shortcut";
            this.createOneShortcutToolStripMenuItem.Click += new System.EventHandler(this.createOneShortcutToolStripMenuItem_Click);
            // 
            // toolStripMenuItem3
            // 
            this.toolStripMenuItem3.Name = "toolStripMenuItem3";
            this.toolStripMenuItem3.Size = new System.Drawing.Size(240, 6);
            // 
            // autoOpenToolStripMenuItem
            // 
            this.autoOpenToolStripMenuItem.Name = "autoOpenToolStripMenuItem";
            this.autoOpenToolStripMenuItem.Size = new System.Drawing.Size(243, 22);
            this.autoOpenToolStripMenuItem.Text = "&Auto-open...";
            this.autoOpenToolStripMenuItem.Click += new System.EventHandler(this.autoOpenToolStripMenuItem_Click);
            // 
            // helpToolStripMenuItem
            // 
            this.helpToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.aboutToolStripMenuItem,
            this.websiteToolStripMenuItem});
            this.helpToolStripMenuItem.Name = "helpToolStripMenuItem";
            this.helpToolStripMenuItem.Size = new System.Drawing.Size(44, 20);
            this.helpToolStripMenuItem.Text = "&Help";
            // 
            // aboutToolStripMenuItem
            // 
            this.aboutToolStripMenuItem.Name = "aboutToolStripMenuItem";
            this.aboutToolStripMenuItem.Size = new System.Drawing.Size(116, 22);
            this.aboutToolStripMenuItem.Text = "&About";
            this.aboutToolStripMenuItem.Click += new System.EventHandler(this.aboutToolStripMenuItem_Click);
            // 
            // websiteToolStripMenuItem
            // 
            this.websiteToolStripMenuItem.Name = "websiteToolStripMenuItem";
            this.websiteToolStripMenuItem.Size = new System.Drawing.Size(116, 22);
            this.websiteToolStripMenuItem.Text = "&Website";
            this.websiteToolStripMenuItem.Click += new System.EventHandler(this.websiteToolStripMenuItem_Click);
            // 
            // btn1
            // 
            this.btn1.Location = new System.Drawing.Point(26, 47);
            this.btn1.Name = "btn1";
            this.btn1.Size = new System.Drawing.Size(258, 56);
            this.btn1.TabIndex = 1;
            this.btn1.Text = "1) Transform URL shortcuts into JPEG screenshots";
            this.btn1.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            this.btn1.UseVisualStyleBackColor = true;
            this.btn1.Click += new System.EventHandler(this.btn1_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(30, 119);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(219, 13);
            this.label1.TabIndex = 2;
            this.label1.Text = "2) Organize/sort the JPEG images in Explorer";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(30, 164);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(242, 13);
            this.label2.TabIndex = 2;
            this.label2.Text = "3) Drag a JPEG here to open webpage in browser";
            // 
            // lblStatus
            // 
            this.lblStatus.AutoSize = true;
            this.lblStatus.Location = new System.Drawing.Point(63, 195);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(0, 13);
            this.lblStatus.TabIndex = 3;
            // 
            // timerUpdateStatus
            // 
            this.timerUpdateStatus.Enabled = true;
            this.timerUpdateStatus.Interval = 400;
            this.timerUpdateStatus.Tick += new System.EventHandler(this.timerUpdateStatus_Tick);
            // 
            // jpegIntoShortcutToolStripMenuItem
            // 
            this.jpegIntoShortcutToolStripMenuItem.Name = "jpegIntoShortcutToolStripMenuItem";
            this.jpegIntoShortcutToolStripMenuItem.Size = new System.Drawing.Size(243, 22);
            this.jpegIntoShortcutToolStripMenuItem.Text = "Jpeg &into shortcut";
            this.jpegIntoShortcutToolStripMenuItem.Click += new System.EventHandler(this.jpegIntoShortcutToolStripMenuItem_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(310, 217);
            this.Controls.Add(this.lblStatus);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.btn1);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.Text = "Bookmarkbucket";
            this.DragDrop += new System.Windows.Forms.DragEventHandler(this.Form1_DragDrop);
            this.DragEnter += new System.Windows.Forms.DragEventHandler(this.Form1_DragEnter);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem fileToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem toolsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem helpToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem createFromURLShortcutsToolStripMenuItem;
        private System.Windows.Forms.ToolStripSeparator toolStripMenuItem1;
        private System.Windows.Forms.ToolStripMenuItem exitToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem websiteToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem aboutToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exportToXmlToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exportToURLShortcutsToolStripMenuItem;
        private System.Windows.Forms.Button btn1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ToolStripMenuItem createFromXmlFileToolStripMenuItem;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.ToolStripSeparator toolStripMenuItem2;
        private System.Windows.Forms.ToolStripMenuItem autoOpenToolStripMenuItem;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Timer timerUpdateStatus;
        private System.Windows.Forms.ToolStripMenuItem createOneShortcutToolStripMenuItem;
        private System.Windows.Forms.ToolStripSeparator toolStripMenuItem3;
        private System.Windows.Forms.ToolStripMenuItem jpegIntoShortcutToolStripMenuItem;
    }
}

