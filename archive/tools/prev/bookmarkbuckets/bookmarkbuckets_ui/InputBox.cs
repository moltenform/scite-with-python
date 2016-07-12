using System;
using System.Drawing;
using System.Collections;
using System.ComponentModel;
using System.Windows.Forms;

    // from http://74.125.113.132/search?q=cache:sFL1PnMV-9MJ:www.java2s.com/Code/CSharp/GUI-Windows-Form/Defineyourowndialogboxandgetuserinput.htm+c%23+simple+input+dialog&cd=5&hl=en&ct=clnk&gl=us&client=firefox-a
    public class InputBoxForm : System.Windows.Forms.Form
    {
        public static string GetStrInput(string strPrompt, string strCurrent)
        {
            InputBoxForm myForm = new InputBoxForm();
            myForm.label1.Text = strPrompt;
            myForm.txtMessage.Text = strCurrent;
            myForm.ShowDialog(new Form());
            if (myForm.DialogResult == DialogResult.OK)
                return (myForm.Message);
            else
                return null;
        }
        public static bool GetDouble(string strPrompt, double fCurrent, out double value)
        {
            value = 0.0;
            string s = GetStrInput(strPrompt, fCurrent.ToString());
            if (s==null||s=="") return false;
            return double.TryParse(s, out value);
        }
        public static bool GetInt(string strPrompt, int nCurrent, out int value)
        {
            value = 0;
            string s = GetStrInput(strPrompt, nCurrent.ToString());
            if (s==null||s=="") return false;
            return int.TryParse(s, out value);
        }

        private System.ComponentModel.Container components=null;
        private System.Windows.Forms.Button btnCancel;
        private System.Windows.Forms.Button btnOK;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox txtMessage;

        public InputBoxForm()
        {
            InitializeComponent();
            this.StartPosition = FormStartPosition.CenterParent;
            this.Text = " ";
        }

        private string strMessage;
        public string Message
        {
            get { return strMessage; }
            set
            {
                strMessage = value;
                txtMessage.Text = strMessage;
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                if (components != null)
                {
                    components.Dispose();
                }
            }
            base.Dispose(disposing);
        }


        #region Windows Form Designer generated code
        private void InitializeComponent()
        {
            this.label1 = new System.Windows.Forms.Label();
            this.btnOK = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.txtMessage = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.Location = new System.Drawing.Point(12, 8);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(240, 48);
            this.label1.TabIndex = 1;
            this.label1.Text = "Type in your message.";
            // 
            // btnOK
            // 
            this.btnOK.DialogResult = System.Windows.Forms.DialogResult.OK;
            this.btnOK.Location = new System.Drawing.Point(102, 104);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new System.Drawing.Size(70, 24);
            this.btnOK.TabIndex = 2;
            this.btnOK.Text = "OK";
            this.btnOK.Click += new System.EventHandler(this.btnOK_Click);
            // 
            // btnCancel
            // 
            this.btnCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.btnCancel.Location = new System.Drawing.Point(178, 104);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(70, 24);
            this.btnCancel.TabIndex = 3;
            this.btnCancel.Text = "Cancel";
            // 
            // txtMessage
            // 
            this.txtMessage.Location = new System.Drawing.Point(16, 72);
            this.txtMessage.Name = "txtMessage";
            this.txtMessage.Size = new System.Drawing.Size(232, 20);
            this.txtMessage.TabIndex = 0;
            // 
            // InputBoxForm
            // 
            this.AcceptButton = this.btnOK;
            this.AutoScaleBaseSize = new System.Drawing.Size(5, 13);
            this.CancelButton = this.btnCancel;
            this.ClientSize = new System.Drawing.Size(260, 139);
            this.ControlBox = false;
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnOK);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.txtMessage);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "InputBoxForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Some Custom Dialog";
            this.ResumeLayout(false);
            this.PerformLayout();

        }
        #endregion

        protected void btnOK_Click(object sender, System.EventArgs e)
        {
            // OK button clicked.
            // get new message.
            strMessage = txtMessage.Text;
        }
    }
