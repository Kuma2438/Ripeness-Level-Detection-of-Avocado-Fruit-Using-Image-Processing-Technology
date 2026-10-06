#!/usr/bin/env python3
"""Builds a native Windows Setup Installer (AvocadoInspector-Setup.exe) from the standalone package."""

import os
from pathlib import Path
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


CSHARP_INSTALLER_SOURCE = r"""using System;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace AvocadoInspectorInstaller
{
    public class SetupForm : Form
    {
        private Label lblTitle;
        private Label lblDesc;
        private Label lblPath;
        private TextBox txtPath;
        private Button btnBrowse;
        private CheckBox chkDesktopShortcut;
        private CheckBox chkStartMenuShortcut;
        private CheckBox chkLaunchNow;
        private Button btnInstall;
        private Button btnCancel;
        private ProgressBar progressBar;
        private Label lblStatus;
        private Panel headerPanel;

        private string defaultInstallDir;

        public SetupForm()
        {
            this.Text = "Avocado Ripeness Inspector Setup";
            this.Size = new Size(580, 440);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(245, 246, 248);

            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            defaultInstallDir = Path.Combine(localAppData, "AvocadoInspector");

            InitializeComponents();
        }

        private void InitializeComponents()
        {
            headerPanel = new Panel();
            headerPanel.Size = new Size(580, 75);
            headerPanel.Location = new Point(0, 0);
            headerPanel.BackColor = Color.FromArgb(33, 43, 54);

            lblTitle = new Label();
            lblTitle.Text = "🥑 Avocado Ripeness & Variety Inspector";
            lblTitle.Font = new Font("Segoe UI", 13, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(46, 204, 113);
            lblTitle.Location = new Point(20, 15);
            lblTitle.AutoSize = true;
            headerPanel.Controls.Add(lblTitle);

            Label lblSubtitle = new Label();
            lblSubtitle.Text = "Setup Wizard - Install Standalone Application";
            lblSubtitle.Font = new Font("Segoe UI", 9, FontStyle.Regular);
            lblSubtitle.ForeColor = Color.FromArgb(180, 190, 200);
            lblSubtitle.Location = new Point(23, 42);
            lblSubtitle.AutoSize = true;
            headerPanel.Controls.Add(lblSubtitle);

            this.Controls.Add(headerPanel);

            lblDesc = new Label();
            lblDesc.Text = "This wizard will install Avocado Ripeness & Variety Inspector on your computer.";
            lblDesc.Font = new Font("Segoe UI", 9, FontStyle.Regular);
            lblDesc.Location = new Point(25, 90);
            lblDesc.Size = new Size(520, 30);
            this.Controls.Add(lblDesc);

            lblPath = new Label();
            lblPath.Text = "Destination Folder:";
            lblPath.Font = new Font("Segoe UI", 9, FontStyle.Bold);
            lblPath.Location = new Point(25, 125);
            lblPath.AutoSize = true;
            this.Controls.Add(lblPath);

            txtPath = new TextBox();
            txtPath.Text = defaultInstallDir;
            txtPath.Font = new Font("Segoe UI", 9);
            txtPath.Location = new Point(25, 148);
            txtPath.Size = new Size(410, 24);
            this.Controls.Add(txtPath);

            btnBrowse = new Button();
            btnBrowse.Text = "Browse...";
            btnBrowse.Font = new Font("Segoe UI", 9);
            btnBrowse.Location = new Point(445, 146);
            btnBrowse.Size = new Size(95, 27);
            btnBrowse.Click += (s, e) => {
                using (FolderBrowserDialog dlg = new FolderBrowserDialog())
                {
                    dlg.SelectedPath = txtPath.Text;
                    if (dlg.ShowDialog() == DialogResult.OK)
                    {
                        txtPath.Text = dlg.SelectedPath;
                    }
                }
            };
            this.Controls.Add(btnBrowse);

            chkDesktopShortcut = new CheckBox();
            chkDesktopShortcut.Text = "Create a Desktop shortcut";
            chkDesktopShortcut.Font = new Font("Segoe UI", 9);
            chkDesktopShortcut.Checked = true;
            chkDesktopShortcut.Location = new Point(25, 190);
            chkDesktopShortcut.AutoSize = true;
            this.Controls.Add(chkDesktopShortcut);

            chkStartMenuShortcut = new CheckBox();
            chkStartMenuShortcut.Text = "Create a Start Menu shortcut";
            chkStartMenuShortcut.Font = new Font("Segoe UI", 9);
            chkStartMenuShortcut.Checked = true;
            chkStartMenuShortcut.Location = new Point(25, 215);
            chkStartMenuShortcut.AutoSize = true;
            this.Controls.Add(chkStartMenuShortcut);

            chkLaunchNow = new CheckBox();
            chkLaunchNow.Text = "Launch Avocado Inspector after installation";
            chkLaunchNow.Font = new Font("Segoe UI", 9, FontStyle.Bold);
            chkLaunchNow.Checked = true;
            chkLaunchNow.Location = new Point(25, 240);
            chkLaunchNow.AutoSize = true;
            this.Controls.Add(chkLaunchNow);

            progressBar = new ProgressBar();
            progressBar.Location = new Point(25, 280);
            progressBar.Size = new Size(515, 22);
            progressBar.Style = ProgressBarStyle.Marquee;
            progressBar.Visible = false;
            this.Controls.Add(progressBar);

            lblStatus = new Label();
            lblStatus.Text = "Ready to install.";
            lblStatus.Font = new Font("Segoe UI", 8.5f, FontStyle.Italic);
            lblStatus.ForeColor = Color.FromArgb(100, 100, 100);
            lblStatus.Location = new Point(25, 308);
            lblStatus.Size = new Size(515, 20);
            this.Controls.Add(lblStatus);

            btnInstall = new Button();
            btnInstall.Text = "Install";
            btnInstall.Font = new Font("Segoe UI", 10, FontStyle.Bold);
            btnInstall.BackColor = Color.FromArgb(46, 204, 113);
            btnInstall.ForeColor = Color.White;
            btnInstall.FlatStyle = FlatStyle.Flat;
            btnInstall.FlatAppearance.BorderSize = 0;
            btnInstall.Location = new Point(330, 345);
            btnInstall.Size = new Size(105, 35);
            btnInstall.Click += BtnInstall_Click;
            this.Controls.Add(btnInstall);

            btnCancel = new Button();
            btnCancel.Text = "Cancel";
            btnCancel.Font = new Font("Segoe UI", 9);
            btnCancel.Location = new Point(445, 345);
            btnCancel.Size = new Size(95, 35);
            btnCancel.Click += (s, e) => { this.Close(); };
            this.Controls.Add(btnCancel);
        }

        private void BtnInstall_Click(object sender, EventArgs e)
        {
            string installPath = txtPath.Text.Trim();
            if (string.IsNullOrEmpty(installPath))
            {
                MessageBox.Show("Please specify a valid installation folder.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            btnInstall.Enabled = false;
            btnBrowse.Enabled = false;
            txtPath.Enabled = false;
            chkDesktopShortcut.Enabled = false;
            chkStartMenuShortcut.Enabled = false;
            progressBar.Visible = true;
            lblStatus.Text = "Extracting files and installing application...";

            bool createDesk = chkDesktopShortcut.Checked;
            bool createStart = chkStartMenuShortcut.Checked;
            bool launch = chkLaunchNow.Checked;

            Thread worker = new Thread(() => {
                try
                {
                    DoInstall(installPath, createDesk, createStart);
                    this.Invoke((MethodInvoker)delegate {
                        progressBar.Visible = false;
                        lblStatus.Text = "Installation completed successfully!";
                        MessageBox.Show("Avocado Ripeness & Variety Inspector has been successfully installed!", "Setup Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);

                        if (launch)
                        {
                            string exePath = Path.Combine(installPath, "avocado-inspector.exe");
                            if (File.Exists(exePath))
                            {
                                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo {
                                    FileName = exePath,
                                    WorkingDirectory = installPath
                                });
                            }
                        }
                        this.Close();
                    });
                }
                catch (Exception ex)
                {
                    this.Invoke((MethodInvoker)delegate {
                        progressBar.Visible = false;
                        lblStatus.Text = "Installation failed!";
                        btnInstall.Enabled = true;
                        MessageBox.Show("Installation failed: " + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    });
                }
            });
            worker.IsBackground = true;
            worker.Start();
        }

        private void DoInstall(string targetDir, bool createDesktopShortcut, bool createStartMenuShortcut)
        {
            if (!Directory.Exists(targetDir))
            {
                Directory.CreateDirectory(targetDir);
            }

            Assembly assembly = Assembly.GetExecutingAssembly();
            string resourceName = null;
            foreach (string name in assembly.GetManifestResourceNames())
            {
                if (name.EndsWith(".zip", StringComparison.OrdinalIgnoreCase))
                {
                    resourceName = name;
                    break;
                }
            }

            if (string.IsNullOrEmpty(resourceName))
            {
                throw new FileNotFoundException("Embedded installation payload not found.");
            }

            string tempZip = Path.Combine(Path.GetTempPath(), "avocado_setup_" + Guid.NewGuid().ToString("N") + ".zip");
            using (Stream input = assembly.GetManifestResourceStream(resourceName))
            using (FileStream output = new FileStream(tempZip, FileMode.Create, FileAccess.Write))
            {
                input.CopyTo(output);
            }

            try
            {
                using (ZipArchive archive = ZipFile.OpenRead(tempZip))
                {
                    foreach (ZipArchiveEntry entry in archive.Entries)
                    {
                        string entryName = entry.FullName;
                        // Strip leading avocado-inspector folder if present
                        if (entryName.StartsWith("avocado-inspector/", StringComparison.OrdinalIgnoreCase) ||
                            entryName.StartsWith("avocado-inspector\\", StringComparison.OrdinalIgnoreCase))
                        {
                            entryName = entryName.Substring("avocado-inspector/".Length);
                        }

                        if (string.IsNullOrEmpty(entryName)) continue;

                        string destinationPath = Path.GetFullPath(Path.Combine(targetDir, entryName));
                        if (entry.FullName.EndsWith("/") || entry.FullName.EndsWith("\\"))
                        {
                            Directory.CreateDirectory(destinationPath);
                        }
                        else
                        {
                            Directory.CreateDirectory(Path.GetDirectoryName(destinationPath));
                            entry.ExtractToFile(destinationPath, true);
                        }
                    }
                }
            }
            finally
            {
                try { File.Delete(tempZip); } catch { }
            }

            string exeFile = Path.Combine(targetDir, "avocado-inspector.exe");

            if (createDesktopShortcut && File.Exists(exeFile))
            {
                string deskPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory), "Avocado Ripeness Inspector.lnk");
                CreateShortcut(deskPath, exeFile, targetDir);
            }

            if (createStartMenuShortcut && File.Exists(exeFile))
            {
                string progPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), "Avocado Inspector");
                Directory.CreateDirectory(progPath);
                string startLnk = Path.Combine(progPath, "Avocado Ripeness Inspector.lnk");
                CreateShortcut(startLnk, exeFile, targetDir);
            }
        }

        private void CreateShortcut(string shortcutPath, string targetExe, string workDir)
        {
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic shortcut = shell.CreateShortcut(shortcutPath);
                shortcut.TargetPath = targetExe;
                shortcut.WorkingDirectory = workDir;
                shortcut.Description = "Avocado Ripeness & Variety Inspector";
                shortcut.Save();
            }
            catch { }
        }
    }

    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new SetupForm());
        }
    }
}
"""


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    package_dir = project_root / "package"
    package_dir.mkdir(parents=True, exist_ok=True)

    zip_file = package_dir / "avocado-inspector-windows-x64.zip"
    if not zip_file.is_file():
        print("[-] Zip package not found. Creating zip archive first...")
        src_dir = package_dir / "avocado-inspector"
        if not src_dir.is_dir():
            print(f"[-] Source directory {src_dir} does not exist. Run build_standalone.py first.")
            sys.exit(1)
        import shutil
        shutil.make_archive(str(package_dir / "avocado-inspector-windows-x64"), "zip", str(src_dir))

    print("=========================================================================")
    print("  AVOCADO INSPECTOR - WINDOWS SETUP INSTALLER BUILDER (.NET C#)")
    print("=========================================================================")

    # Write C# installer code
    cs_file = package_dir / "Installer.cs"
    with open(cs_file, "w", encoding="utf-8") as f:
        f.write(CSHARP_INSTALLER_SOURCE)

    setup_exe = package_dir / "AvocadoInspector-Setup.exe"

    csc_compiler = Path(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe")
    if not csc_compiler.is_file():
        csc_compiler = Path(r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe")

    if not csc_compiler.is_file():
        print("[-] C# compiler (csc.exe) not found on system.", file=sys.stderr)
        sys.exit(1)

    dotnet_dir = csc_compiler.parent
    compression_dll = dotnet_dir / "System.IO.Compression.FileSystem.dll"
    core_compression_dll = dotnet_dir / "System.IO.Compression.dll"

    cmd = [
        str(csc_compiler),
        "/target:winexe",
        "/platform:x64",
        "/optimize+",
        f"/out:{setup_exe}",
        f"/resource:{zip_file},payload.zip",
        f"/reference:{compression_dll}",
        f"/reference:{core_compression_dll}",
        "/reference:System.Windows.Forms.dll",
        "/reference:System.Drawing.dll",
        "/reference:Microsoft.CSharp.dll",
        str(cs_file),
    ]

    print("[*] Compiling native Windows Setup Installer...")
    ret = subprocess.call(cmd)

    if ret == 0 and setup_exe.is_file():
        print("\n=========================================================================")
        print("[+] Windows Setup Installer successfully created!")
        print(f"[+] Installer Path: {setup_exe}")
        print(f"[+] File Size: {setup_exe.stat().st_size / (1024 * 1024):.1f} MB")
        print("=========================================================================")
        try:
            os.remove(cs_file)
        except Exception:
            pass
    else:
        print("[-] Failed to compile Windows Setup Installer.", file=sys.stderr)
        sys.exit(ret)


if __name__ == "__main__":
    main()
