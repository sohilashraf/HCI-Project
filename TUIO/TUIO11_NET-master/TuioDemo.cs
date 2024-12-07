/*
	TUIO C# Demo - part of the reacTIVision project
	Copyright (c) 2005-2016 Martin Kaltenbrunner <martin@tuio.org>

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

using System;
using System.Drawing;
using System.Windows.Forms;
using System.ComponentModel;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using TUIO;
using System.IO;
using System.Drawing.Drawing2D;

public class TuioDemo : Form, TuioListener
{
    private TuioClient client;
    private Dictionary<long, TuioObject> objectList;
    private Dictionary<long, TuioCursor> cursorList;
    private Dictionary<long, TuioBlob> blobList;

    // Variables for the socket client
    private const string serverIp = "127.0.0.1"; // Python server IP
    private const int serverPort = 65482;        // Python server port
    private TcpClient tcpClient;
    private NetworkStream stream;
    private byte[] sendBuffer = new byte[1024];
    private byte[] receiveBuffer = new byte[1024];

    public static int width, height;
    private int window_width = 20;
    private int window_height = 20;

    private int window_left = 0;
    private int window_top = 0;
    private int screen_width = Screen.PrimaryScreen.Bounds.Width;
    private int screen_height = Screen.PrimaryScreen.Bounds.Height;

    private bool fullscreen;
    private bool verbose;

    Font font = new Font("Arial", 10.0f);
    SolidBrush fntBrush = new SolidBrush(Color.White);
    SolidBrush bgrBrush = new SolidBrush(Color.FromArgb(0, 0, 64));
    SolidBrush curBrush = new SolidBrush(Color.FromArgb(192, 0, 192));
    SolidBrush objBrush = new SolidBrush(Color.FromArgb(64, 0, 0));
    SolidBrush blbBrush = new SolidBrush(Color.FromArgb(64, 64, 64));
    Pen curPen = new Pen(new SolidBrush(Color.Blue), 1);
    private string objectImagePath;
    private string backgroundImagePath;
    public int flagA = 0;


    public TuioDemo(int port)
    {
        verbose = false;
        fullscreen = false;
        width = window_width;
        height = window_height;

        this.ClientSize = new System.Drawing.Size(width, height);
        //this.Name = "TuioDemo";
        //this.Text = "TuioDemo";

        this.Closing += new CancelEventHandler(Form_Closing);
        this.KeyDown += new KeyEventHandler(Form_KeyDown);

        this.SetStyle(ControlStyles.AllPaintingInWmPaint |
                        ControlStyles.UserPaint |
                        ControlStyles.DoubleBuffer, true);

        objectList = new Dictionary<long, TuioObject>(128);
        cursorList = new Dictionary<long, TuioCursor>(128);
        blobList = new Dictionary<long, TuioBlob>(128);

        client = new TuioClient(port);
        client.addTuioListener(this);

        client.connect();

        // Initialize socket client connection to Python server
        InitializeSocketClient();
    }
    private void InitializeSocketClient()
    {
        try
        {
            tcpClient = new TcpClient(serverIp, serverPort);
            stream = tcpClient.GetStream();
            Console.WriteLine("Connected to Python server at " + serverIp + ":" + serverPort);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error connecting to server: " + ex.Message);
        }
    }
    private void SendToServer(string message)

    {
        if (tcpClient.Connected)
        {
            sendBuffer = Encoding.UTF8.GetBytes(message);
            stream.Write(sendBuffer, 0, sendBuffer.Length);
            Console.WriteLine("Sent to server: " + message);
        }
        else
        {
            Console.WriteLine("Not connected to server.");
        }
    }
    private void ReceiveFromServer()
    {
        if (tcpClient.Connected)
        {
            int bytesRead = stream.Read(receiveBuffer, 0, receiveBuffer.Length);
            string response = Encoding.UTF8.GetString(receiveBuffer, 0, bytesRead);
            this.Text = "Received from server: " + response;
        }
    }
    private void Form_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e)
    {
        if (e.KeyData == Keys.F1)
        {
            if (fullscreen == false)
            {
                width = screen_width;
                height = screen_height;

                window_left = this.Left;
                window_top = this.Top;

                this.FormBorderStyle = FormBorderStyle.None;
                this.Left = 0;
                this.Top = 0;
                this.Width = screen_width;
                this.Height = screen_height;

                fullscreen = true;
            }
            else
            {
                width = window_width;
                height = window_height;

                this.FormBorderStyle = FormBorderStyle.Sizable;
                this.Left = window_left;
                this.Top = window_top;
                this.Width = window_width;
                this.Height = window_height;

                fullscreen = false;
            }
        }
        else if (e.KeyData == Keys.Escape)
        {
            this.Close();
        }
        else if (e.KeyData == Keys.V)
        {
            verbose = !verbose;
        }
    }

    private void Form_Closing(object sender, System.ComponentModel.CancelEventArgs e)
    {
        client.removeTuioListener(this);
        client.disconnect();

        // Close the socket connection to the Python server
        if (tcpClient.Connected)
        {
            stream.Close();
            tcpClient.Close();
            Console.WriteLine("Disconnected from Python server.");
        }

        System.Environment.Exit(0);
    }

    public void addTuioObject(TuioObject o)
    {
        lock (objectList)
        {
            objectList.Add(o.SessionID, o);
        }
        if (verbose) Console.WriteLine("add obj " + o.SymbolID + " (" + o.SessionID + ") " + o.X + " " + o.Y + " " + o.Angle);
    }

    public void updateTuioObject(TuioObject o)
    {

        if (verbose) Console.WriteLine("set obj " + o.SymbolID + " " + o.SessionID + " " + o.X + " " + o.Y + " " + o.Angle + " " + o.MotionSpeed + " " + o.RotationSpeed + " " + o.MotionAccel + " " + o.RotationAccel);
    }

    public void removeTuioObject(TuioObject o)
    {
        lock (objectList)
        {
            objectList.Remove(o.SessionID);
        }
        if (verbose) Console.WriteLine("del obj " + o.SymbolID + " (" + o.SessionID + ")");
    }

    public void addTuioCursor(TuioCursor c)
    {
        lock (cursorList)
        {
            cursorList.Add(c.SessionID, c);
        }
        if (verbose) Console.WriteLine("add cur " + c.CursorID + " (" + c.SessionID + ") " + c.X + " " + c.Y);
    }

    public void updateTuioCursor(TuioCursor c)
    {
        if (verbose) Console.WriteLine("set cur " + c.CursorID + " (" + c.SessionID + ") " + c.X + " " + c.Y + " " + c.MotionSpeed + " " + c.MotionAccel);
    }

    public void removeTuioCursor(TuioCursor c)
    {
        lock (cursorList)
        {
            cursorList.Remove(c.SessionID);
        }
        if (verbose) Console.WriteLine("del cur " + c.CursorID + " (" + c.SessionID + ")");
    }

    public void addTuioBlob(TuioBlob b)
    {
        lock (blobList)
        {
            blobList.Add(b.SessionID, b);
        }
        if (verbose) Console.WriteLine("add blb " + b.BlobID + " (" + b.SessionID + ") " + b.X + " " + b.Y + " " + b.Angle + " " + b.Width + " " + b.Height + " " + b.Area);
    }

    public void updateTuioBlob(TuioBlob b)
    {

        if (verbose) Console.WriteLine("set blb " + b.BlobID + " (" + b.SessionID + ") " + b.X + " " + b.Y + " " + b.Angle + " " + b.Width + " " + b.Height + " " + b.Area + " " + b.MotionSpeed + " " + b.RotationSpeed + " " + b.MotionAccel + " " + b.RotationAccel);
    }

    public void removeTuioBlob(TuioBlob b)
    {
        lock (blobList)
        {
            blobList.Remove(b.SessionID);
        }
        if (verbose) Console.WriteLine("del blb " + b.BlobID + " (" + b.SessionID + ")");
    }

    public void refresh(TuioTime frameTime)
    {
        Invalidate();
    }

    protected override void OnPaintBackground(PaintEventArgs pevent)
    {
        // Getting the graphics object
        Graphics g = pevent.Graphics;
        string backgpath = "bgg.jpeg";// the background image 

        if (flagA > 0)
        {
            backgpath = "";// the background image
        }
        if (File.Exists(backgpath))
        {
            using (Image bggimage = Image.FromFile(backgpath))
            {
                g.DrawImage(bggimage, new Rectangle(0, 0, width, height));
            }
        }
        // draw the cursor path
        if (cursorList.Count > 0)
        {
            lock (cursorList)
            {
                foreach (TuioCursor tcur in cursorList.Values)
                {
                    List<TuioPoint> path = tcur.Path;
                    TuioPoint current_point = path[0];

                    for (int i = 0; i < path.Count; i++)
                    {
                        TuioPoint next_point = path[i];
                        g.DrawLine(curPen, current_point.getScreenX(width), current_point.getScreenY(height), next_point.getScreenX(width), next_point.getScreenY(height));
                        current_point = next_point;
                    }
                    g.FillEllipse(curBrush, current_point.getScreenX(width) - height / 100, current_point.getScreenY(height) - height / 100, height / 50, height / 50);
                    g.DrawString(tcur.CursorID + "", font, fntBrush, new PointF(tcur.getScreenX(width) - 10, tcur.getScreenY(height) - 10));
                }
            }

        }
        // draw the objects
        if (objectList.Count > 0)
        {
            lock (objectList)
            {
                foreach (TuioObject tobj in objectList.Values)
                {
                    int ox = 250;
                    int oy = 450;
                    int baseSize = height / 5; // Base size of the object

                    // Define min and max scaling limits
                    float minScale = 0.5f;  // Minimum 50% of the original size
                    float maxScale = 2.0f;  // Maximum 200% of the original size

                    // Normalize the angle to a value between -1 and 1
                    float normalizedAngle = (float)(tobj.Angle / Math.PI); // Normalized between -1 (left) and +1 (right)

                    // Smooth scaling: Bigger when rotating right, smaller when rotating left
                    float scale = minScale + (maxScale - minScale) * (1 + normalizedAngle) / 2;

                    // Adjust the object size based on the scaling factor
                    int size = (int)(baseSize * scale);
                    string m = tobj.SymbolID + " " + tobj.Angle;

                    this.Text = m;
                    SendToServer(m);

                    // Draw the object image without rotation
                    switch (tobj.SymbolID)
                    {
                        case 0:
                            flagA = 1;
                            break;
                        case 1:
                            flagA = 2;
                            break;
                    }

                    if (flagA == 1)
                    {
                        switch (tobj.SymbolID)
                        {
                            case 2:

                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "11.png");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d5.jpeg");
                                m = tobj.SymbolID + "";
                                this.Text = m;
                                SendToServer(m);

                                break;
                            case 3:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "7atshbsot.png");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d3.jpeg");
                                break;
                            case 4:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "5afr3.png");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d2.jpeg");
                                break;
                            case 5:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "khofo.png");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d4.jpeg");
                                break;
                            case 6:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "ramsis.png");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d1.jpeg");
                                break;

                        }
                    }
                    if (flagA == 2)
                    {
                        switch (tobj.SymbolID)
                        {
                            case 2:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "s1.jpeg");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d1.jpeg");

                                break;
                            case 3:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "s2.jpeg");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d2.jpeg");
                                break;
                            case 4:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "s3.jpeg");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d3.jpeg");
                                break;
                            case 5:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "s4.jpeg");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d4.jpeg");
                                break;
                            case 6:
                                objectImagePath = Path.Combine(Environment.CurrentDirectory, "s5.jpeg");
                                backgroundImagePath = Path.Combine(Environment.CurrentDirectory, "d5.jpeg");
                                break;

                        }
                    }

                    try
                    {
                        // Draw the background image without rotation
                        if (File.Exists(backgroundImagePath))
                        {
                            using (Image bgImage = Image.FromFile(backgroundImagePath))
                            {
                                g.DrawImage(bgImage, new Rectangle(new Point(0, 0), new Size(width, height)));
                            }
                        }
                        else
                        {
                            Console.WriteLine($"Background image not found: {backgroundImagePath}");
                        }

                        // Draw the object image without rotation, but with scaling
                        if (File.Exists(objectImagePath))
                        {
                            using (Image objectImage = Image.FromFile(objectImagePath))
                            {
                                // Save the current state of the graphics object
                                GraphicsState state = g.Save();

                                // Apply scaling without rotation
                                g.DrawImage(objectImage, new Rectangle(ox - size / 2, oy - size / 2, size, size));

                                // Restore the graphics state
                                g.Restore(state);
                            }
                        }
                        else
                        {
                            Console.WriteLine($"Object image not found: {objectImagePath}");
                            // Fall back to drawing a rectangle
                            //g.FillRectangle(objBrush, new Rectangle(ox - size / 2, oy - size / 2, size, size));
                        }
                    }
                    catch { }
                }
            }
        }

        // draw the blobs
        if (blobList.Count > 0)
        {
            lock (blobList)
            {
                foreach (TuioBlob tblb in blobList.Values)
                {
                    int bx = tblb.getScreenX(width);
                    int by = tblb.getScreenY(height);
                    float bw = tblb.Width * width;
                    float bh = tblb.Height * height;

                    g.TranslateTransform(bx, by);
                    g.RotateTransform((float)(tblb.Angle / Math.PI * 180.0f));
                    g.TranslateTransform(-bx, -by);

                    g.FillEllipse(blbBrush, bx - bw / 2, by - bh / 2, bw, bh);

                    g.TranslateTransform(bx, by);
                    g.RotateTransform(-1 * (float)(tblb.Angle / Math.PI * 180.0f));
                    g.TranslateTransform(-bx, -by);

                    g.DrawString(tblb.BlobID + "", font, fntBrush, new PointF(bx, by));
                }
            }
        }


    }

    private void InitializeComponent()
    {
        this.SuspendLayout();
        // 
        // TuioDemo
        // 
        this.ClientSize = new System.Drawing.Size(282, 253);
        this.Name = "TuioDemo";
        this.Load += new System.EventHandler(this.TuioDemo_Load);
        this.ResumeLayout(false);

    }

    private void TuioDemo_Load(object sender, EventArgs e)
    {

    }

    public static void Main(String[] argv)
    {
        int port = 0;
        switch (argv.Length)
        {
            case 1:
                port = int.Parse(argv[0], null);
                if (port == 0) goto default;
                break;
            case 0:
                port = 3333;
                break;
            default:
                Console.WriteLine("usage: mono TuioDemo [port]");
                System.Environment.Exit(0);
                break;
        }

        TuioDemo app = new TuioDemo(port);
        Application.Run(app);
    }
}