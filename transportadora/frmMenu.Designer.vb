<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class frmMenu
    Inherits System.Windows.Forms.Form

    'Form reemplaza a Dispose para limpiar la lista de componentes.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Requerido por el Diseñador de Windows Forms
    Private components As System.ComponentModel.IContainer

    'NOTA: el Diseñador de Windows Forms necesita el siguiente procedimiento
    'Se puede modificar usando el Diseñador de Windows Forms.  
    'No lo modifique con el editor de código.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(frmMenu))
        Me.ContextMenuStrip1 = New System.Windows.Forms.ContextMenuStrip(Me.components)
        Me.ContactoToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.MenuStrip1 = New System.Windows.Forms.MenuStrip()
        Me.ContactoToolStripMenuItem1 = New System.Windows.Forms.ToolStripMenuItem()
        Me.DirecciónToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.ConductorToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.ProvinciaToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.DetallePaqueteToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.BusToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.BusConductorToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.PaqueteToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem()
        Me.ContextMenuStrip1.SuspendLayout()
        Me.MenuStrip1.SuspendLayout()
        Me.SuspendLayout()
        '
        'ContextMenuStrip1
        '
        Me.ContextMenuStrip1.ImageScalingSize = New System.Drawing.Size(20, 20)
        Me.ContextMenuStrip1.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.ContactoToolStripMenuItem})
        Me.ContextMenuStrip1.Name = "ContextMenuStrip1"
        Me.ContextMenuStrip1.Size = New System.Drawing.Size(139, 28)
        '
        'ContactoToolStripMenuItem
        '
        Me.ContactoToolStripMenuItem.Name = "ContactoToolStripMenuItem"
        Me.ContactoToolStripMenuItem.Size = New System.Drawing.Size(138, 24)
        Me.ContactoToolStripMenuItem.Text = "Contacto"
        '
        'MenuStrip1
        '
        Me.MenuStrip1.ImageScalingSize = New System.Drawing.Size(60, 60)
        Me.MenuStrip1.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.ContactoToolStripMenuItem1, Me.DirecciónToolStripMenuItem, Me.ConductorToolStripMenuItem, Me.ProvinciaToolStripMenuItem, Me.DetallePaqueteToolStripMenuItem, Me.BusToolStripMenuItem, Me.BusConductorToolStripMenuItem, Me.PaqueteToolStripMenuItem})
        Me.MenuStrip1.Location = New System.Drawing.Point(0, 0)
        Me.MenuStrip1.Name = "MenuStrip1"
        Me.MenuStrip1.Size = New System.Drawing.Size(1280, 68)
        Me.MenuStrip1.TabIndex = 1
        Me.MenuStrip1.Text = "MenuStrip1"
        '
        'ContactoToolStripMenuItem1
        '
        Me.ContactoToolStripMenuItem1.Image = CType(resources.GetObject("ContactoToolStripMenuItem1.Image"), System.Drawing.Image)
        Me.ContactoToolStripMenuItem1.Name = "ContactoToolStripMenuItem1"
        Me.ContactoToolStripMenuItem1.Size = New System.Drawing.Size(143, 64)
        Me.ContactoToolStripMenuItem1.Text = "Contacto"
        '
        'DirecciónToolStripMenuItem
        '
        Me.DirecciónToolStripMenuItem.Image = CType(resources.GetObject("DirecciónToolStripMenuItem.Image"), System.Drawing.Image)
        Me.DirecciónToolStripMenuItem.Name = "DirecciónToolStripMenuItem"
        Me.DirecciónToolStripMenuItem.Size = New System.Drawing.Size(146, 64)
        Me.DirecciónToolStripMenuItem.Text = "Dirección"
        '
        'ConductorToolStripMenuItem
        '
        Me.ConductorToolStripMenuItem.Image = CType(resources.GetObject("ConductorToolStripMenuItem.Image"), System.Drawing.Image)
        Me.ConductorToolStripMenuItem.Name = "ConductorToolStripMenuItem"
        Me.ConductorToolStripMenuItem.Size = New System.Drawing.Size(152, 64)
        Me.ConductorToolStripMenuItem.Text = "Conductor"
        '
        'ProvinciaToolStripMenuItem
        '
        Me.ProvinciaToolStripMenuItem.Image = CType(resources.GetObject("ProvinciaToolStripMenuItem.Image"), System.Drawing.Image)
        Me.ProvinciaToolStripMenuItem.Name = "ProvinciaToolStripMenuItem"
        Me.ProvinciaToolStripMenuItem.Size = New System.Drawing.Size(143, 64)
        Me.ProvinciaToolStripMenuItem.Text = "Provincia"
        '
        'DetallePaqueteToolStripMenuItem
        '
        Me.DetallePaqueteToolStripMenuItem.Image = CType(resources.GetObject("DetallePaqueteToolStripMenuItem.Image"), System.Drawing.Image)
        Me.DetallePaqueteToolStripMenuItem.Name = "DetallePaqueteToolStripMenuItem"
        Me.DetallePaqueteToolStripMenuItem.Size = New System.Drawing.Size(190, 64)
        Me.DetallePaqueteToolStripMenuItem.Text = "Detalle_Paquete"
        '
        'BusToolStripMenuItem
        '
        Me.BusToolStripMenuItem.Image = CType(resources.GetObject("BusToolStripMenuItem.Image"), System.Drawing.Image)
        Me.BusToolStripMenuItem.Name = "BusToolStripMenuItem"
        Me.BusToolStripMenuItem.Size = New System.Drawing.Size(106, 64)
        Me.BusToolStripMenuItem.Text = "Bus"
        '
        'BusConductorToolStripMenuItem
        '
        Me.BusConductorToolStripMenuItem.Image = CType(resources.GetObject("BusConductorToolStripMenuItem.Image"), System.Drawing.Image)
        Me.BusConductorToolStripMenuItem.Name = "BusConductorToolStripMenuItem"
        Me.BusConductorToolStripMenuItem.Size = New System.Drawing.Size(181, 64)
        Me.BusConductorToolStripMenuItem.Text = "Bus_Conductor"
        '
        'PaqueteToolStripMenuItem
        '
        Me.PaqueteToolStripMenuItem.Image = CType(resources.GetObject("PaqueteToolStripMenuItem.Image"), System.Drawing.Image)
        Me.PaqueteToolStripMenuItem.Name = "PaqueteToolStripMenuItem"
        Me.PaqueteToolStripMenuItem.Size = New System.Drawing.Size(136, 64)
        Me.PaqueteToolStripMenuItem.Text = "Paquete"
        '
        'frmMenu
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 17.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.SystemColors.ActiveBorder
        Me.ClientSize = New System.Drawing.Size(1280, 496)
        Me.Controls.Add(Me.MenuStrip1)
        Me.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.MainMenuStrip = Me.MenuStrip1
        Me.Name = "frmMenu"
        Me.Text = "frmMenu"
        Me.ContextMenuStrip1.ResumeLayout(False)
        Me.MenuStrip1.ResumeLayout(False)
        Me.MenuStrip1.PerformLayout()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents ContextMenuStrip1 As ContextMenuStrip
    Friend WithEvents ContactoToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents MenuStrip1 As MenuStrip
    Friend WithEvents ContactoToolStripMenuItem1 As ToolStripMenuItem
    Friend WithEvents DirecciónToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ConductorToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents ProvinciaToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents DetallePaqueteToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents BusToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents BusConductorToolStripMenuItem As ToolStripMenuItem
    Friend WithEvents PaqueteToolStripMenuItem As ToolStripMenuItem
End Class
