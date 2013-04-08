using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Text;
using System.Windows.Forms;

namespace bookmarkbucket_ui
{
    public static class ImageHelper
    {
        private static ImageCodecInfo s_jpgEncoder;
        private static ImageCodecInfo GetEncoder(ImageFormat format)
        {
            ImageCodecInfo[] codecs = ImageCodecInfo.GetImageDecoders();
            foreach (ImageCodecInfo codec in codecs)
            {
                if (codec.FormatID == format.Guid)
                {
                    return codec;
                }
            }
            return null;
        }
        public static Bitmap ResizeImage(Bitmap srcImage, int newWidth, int newHeight) //Kris Erickson, stackoverflow 87753.
        {
            Bitmap newImage = new Bitmap(newWidth, newHeight);
            using (Graphics gr = Graphics.FromImage(newImage))
            {
                gr.SmoothingMode = SmoothingMode.HighQuality;
                gr.InterpolationMode = InterpolationMode.HighQualityBicubic;
                gr.PixelOffsetMode = PixelOffsetMode.HighQuality;
                gr.DrawImage(srcImage, new Rectangle(0, 0, newWidth, newHeight));
            }
            return newImage;
        }
        public static Bitmap ResizeAndTruncateImage(Bitmap srcImage, int maxW, int maxH, float factor, bool bBicubic)
        {
            int newWidth = (int)(factor * srcImage.Width);
            int newHeight = (int)(factor * srcImage.Height);
            Bitmap newImage = new Bitmap(Math.Min(newWidth, maxW), Math.Min(newHeight, maxH));
            using (Graphics gr = Graphics.FromImage(newImage))
            {
                gr.SmoothingMode = SmoothingMode.HighQuality;
                gr.InterpolationMode = bBicubic ? InterpolationMode.HighQualityBicubic : InterpolationMode.HighQualityBilinear;
                gr.PixelOffsetMode = PixelOffsetMode.HighQuality;
                gr.DrawImage(srcImage, new Rectangle(0, 0, newWidth, newHeight));
            }
            return newImage;
        }
        public static Bitmap GetBlankBitmap(int width, int height)
        {
            Bitmap newImage = new Bitmap(width, height);
            using (Graphics gr = Graphics.FromImage(newImage))
            {
                gr.DrawRectangle(new Pen(Color.LightGray), 0, 0, width-1, height-1);
            }
            return newImage;
        }

        public static void BitmapSaveJpegQuality(Bitmap srcImage, string sDest, int nQual) //Dustin Getz, stackoverflow 1484759
        {
            if (nQual < 0 || nQual > 100) throw new Exception("invalid quality specified");
            if (s_jpgEncoder == null)
            {
                s_jpgEncoder = GetEncoder(ImageFormat.Jpeg);
                if (s_jpgEncoder == null) throw new Exception("jpgEncoder not found");
            }
            System.Drawing.Imaging.Encoder myEncoder = System.Drawing.Imaging.Encoder.Quality;
            EncoderParameters myEncoderParameters = new EncoderParameters(1); //array of EncoderParameter objs

            EncoderParameter myEncoderParameter = new EncoderParameter(myEncoder, nQual);
            myEncoderParameters.Param[0] = myEncoderParameter;
            srcImage.Save(sDest, s_jpgEncoder, myEncoderParameters);
        }
        public static string GetOpenString(string sExtension, string sTitle)
        {
            OpenFileDialog dlg = new OpenFileDialog();
            System.Diagnostics.Debug.Assert(!sExtension.Contains("."));
            dlg.Title = sTitle;
            dlg.FileName = ""; // Default file name
            dlg.DefaultExt = "." + sExtension; // Default file extension
            dlg.Filter = "." + sExtension + " documents|*." + sExtension; // Filter files by extension

            DialogResult result = dlg.ShowDialog();
            if (result == DialogResult.OK)
                return dlg.FileName;
            else
                return null;
        }

        public static string GetSaveString(string sExtension, string sTitle)
        {
            SaveFileDialog dlg = new SaveFileDialog();
            System.Diagnostics.Debug.Assert(!sExtension.Contains("."));
            dlg.Title = sTitle;
            dlg.FileName = ""; // Default file name
            dlg.DefaultExt = "." + sExtension; // Default file extension
            dlg.Filter = "." + sExtension + " documents|*." + sExtension; // Filter files by extension

            DialogResult result = dlg.ShowDialog();
            if (result == DialogResult.OK)
                return dlg.FileName;
            else
                return null;
        }


        public static void ResizeAndTruncateAndSaveImage(string sPng, string sJpeg, int maxw, int maxh,float factor, int jpgqual, bool bBicubic)
        {
            using (Bitmap bmpIn = new Bitmap(sPng))
            using (Bitmap bmpOut = ResizeAndTruncateImage(bmpIn, maxw, maxh, factor, bBicubic))
                    BitmapSaveJpegQuality(bmpOut, sJpeg, jpgqual);
        }
    }
}
