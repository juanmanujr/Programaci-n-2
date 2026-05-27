<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class frmPaquete
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(frmPaquete))
        Me.txtDireccion = New System.Windows.Forms.ComboBox()
        Me.cmbProvincia = New System.Windows.Forms.ComboBox()
        Me.cmbConductor = New System.Windows.Forms.ComboBox()
        Me.cmbDetalle = New System.Windows.Forms.ComboBox()
        Me.txtPeso = New System.Windows.Forms.TextBox()
        Me.txtDestinatario = New System.Windows.Forms.TextBox()
        Me.txtCodigo = New System.Windows.Forms.TextBox()
        Me.lbldestinatario = New System.Windows.Forms.Label()
        Me.lblcedula = New System.Windows.Forms.Label()
        Me.lblpeso = New System.Windows.Forms.Label()
        Me.lblcodigo = New System.Windows.Forms.Label()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Lbl_detalle_paquete = New System.Windows.Forms.Label()
        Me.Lblprovincia = New System.Windows.Forms.Label()
        Me.lblconductor = New System.Windows.Forms.Label()
        Me.dgvPaquetes = New System.Windows.Forms.DataGridView()
        Me.CODIGO = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.DESTINARIO = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.PESO = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.CONDUCTOR = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.DIRECCION = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.PROVINCIA = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.DETALLE_PAQUETE = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.Label3 = New System.Windows.Forms.Label()
        Me.Label4 = New System.Windows.Forms.Label()
        Me.Label5 = New System.Windows.Forms.Label()
        Me.Label6 = New System.Windows.Forms.Label()
        Me.btnCerrar = New System.Windows.Forms.Button()
        Me.btnEliminar = New System.Windows.Forms.Button()
        Me.btnModificar = New System.Windows.Forms.Button()
        Me.btnGuardar = New System.Windows.Forms.Button()
        Me.btnNuevo = New System.Windows.Forms.Button()
        CType(Me.dgvPaquetes, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.SuspendLayout()
        '
        'txtDireccion
        '
        Me.txtDireccion.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtDireccion.FormattingEnabled = True
        Me.txtDireccion.Location = New System.Drawing.Point(195, 241)
        Me.txtDireccion.Name = "txtDireccion"
        Me.txtDireccion.Size = New System.Drawing.Size(121, 25)
        Me.txtDireccion.TabIndex = 151
        '
        'cmbProvincia
        '
        Me.cmbProvincia.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.cmbProvincia.FormattingEnabled = True
        Me.cmbProvincia.Location = New System.Drawing.Point(195, 289)
        Me.cmbProvincia.Name = "cmbProvincia"
        Me.cmbProvincia.Size = New System.Drawing.Size(121, 25)
        Me.cmbProvincia.TabIndex = 149
        '
        'cmbConductor
        '
        Me.cmbConductor.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.cmbConductor.FormattingEnabled = True
        Me.cmbConductor.Location = New System.Drawing.Point(195, 201)
        Me.cmbConductor.Name = "cmbConductor"
        Me.cmbConductor.Size = New System.Drawing.Size(121, 25)
        Me.cmbConductor.TabIndex = 148
        '
        'cmbDetalle
        '
        Me.cmbDetalle.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.cmbDetalle.FormattingEnabled = True
        Me.cmbDetalle.Location = New System.Drawing.Point(195, 329)
        Me.cmbDetalle.Name = "cmbDetalle"
        Me.cmbDetalle.Size = New System.Drawing.Size(121, 25)
        Me.cmbDetalle.TabIndex = 150
        '
        'txtPeso
        '
        Me.txtPeso.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtPeso.Location = New System.Drawing.Point(195, 166)
        Me.txtPeso.Margin = New System.Windows.Forms.Padding(4)
        Me.txtPeso.Name = "txtPeso"
        Me.txtPeso.Size = New System.Drawing.Size(121, 25)
        Me.txtPeso.TabIndex = 138
        '
        'txtDestinatario
        '
        Me.txtDestinatario.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtDestinatario.Location = New System.Drawing.Point(195, 136)
        Me.txtDestinatario.Margin = New System.Windows.Forms.Padding(4)
        Me.txtDestinatario.Name = "txtDestinatario"
        Me.txtDestinatario.Size = New System.Drawing.Size(121, 25)
        Me.txtDestinatario.TabIndex = 137
        '
        'txtCodigo
        '
        Me.txtCodigo.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtCodigo.Location = New System.Drawing.Point(195, 103)
        Me.txtCodigo.Margin = New System.Windows.Forms.Padding(4)
        Me.txtCodigo.Name = "txtCodigo"
        Me.txtCodigo.Size = New System.Drawing.Size(121, 25)
        Me.txtCodigo.TabIndex = 136
        '
        'lbldestinatario
        '
        Me.lbldestinatario.AutoSize = True
        Me.lbldestinatario.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lbldestinatario.Location = New System.Drawing.Point(26, 136)
        Me.lbldestinatario.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lbldestinatario.Name = "lbldestinatario"
        Me.lbldestinatario.Size = New System.Drawing.Size(107, 19)
        Me.lbldestinatario.TabIndex = 135
        Me.lbldestinatario.Text = "DESTINATARIO"
        '
        'lblcedula
        '
        Me.lblcedula.AutoSize = True
        Me.lblcedula.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblcedula.Location = New System.Drawing.Point(26, 241)
        Me.lblcedula.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblcedula.Name = "lblcedula"
        Me.lblcedula.Size = New System.Drawing.Size(83, 19)
        Me.lblcedula.TabIndex = 134
        Me.lblcedula.Text = "DIRECCIÓN"
        '
        'lblpeso
        '
        Me.lblpeso.AutoSize = True
        Me.lblpeso.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblpeso.Location = New System.Drawing.Point(26, 166)
        Me.lblpeso.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblpeso.Name = "lblpeso"
        Me.lblpeso.Size = New System.Drawing.Size(44, 19)
        Me.lblpeso.TabIndex = 133
        Me.lblpeso.Text = "PESO"
        '
        'lblcodigo
        '
        Me.lblcodigo.AutoSize = True
        Me.lblcodigo.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblcodigo.Location = New System.Drawing.Point(26, 103)
        Me.lblcodigo.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblcodigo.Name = "lblcodigo"
        Me.lblcodigo.Size = New System.Drawing.Size(64, 19)
        Me.lblcodigo.TabIndex = 132
        Me.lblcodigo.Text = "CÓDIGO"
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Font = New System.Drawing.Font("Segoe UI", 16.2!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label1.Location = New System.Drawing.Point(584, 29)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(155, 38)
        Me.Label1.TabIndex = 131
        Me.Label1.Text = "PAQUETES"
        '
        'Lbl_detalle_paquete
        '
        Me.Lbl_detalle_paquete.AutoSize = True
        Me.Lbl_detalle_paquete.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Lbl_detalle_paquete.Location = New System.Drawing.Point(26, 336)
        Me.Lbl_detalle_paquete.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.Lbl_detalle_paquete.Name = "Lbl_detalle_paquete"
        Me.Lbl_detalle_paquete.Size = New System.Drawing.Size(131, 19)
        Me.Lbl_detalle_paquete.TabIndex = 147
        Me.Lbl_detalle_paquete.Text = "DETALLE_PAQUETE"
        '
        'Lblprovincia
        '
        Me.Lblprovincia.AutoSize = True
        Me.Lblprovincia.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Lblprovincia.Location = New System.Drawing.Point(26, 289)
        Me.Lblprovincia.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.Lblprovincia.Name = "Lblprovincia"
        Me.Lblprovincia.Size = New System.Drawing.Size(85, 19)
        Me.Lblprovincia.TabIndex = 146
        Me.Lblprovincia.Text = "PROVINCIA"
        '
        'lblconductor
        '
        Me.lblconductor.AutoSize = True
        Me.lblconductor.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblconductor.Location = New System.Drawing.Point(26, 201)
        Me.lblconductor.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblconductor.Name = "lblconductor"
        Me.lblconductor.Size = New System.Drawing.Size(96, 19)
        Me.lblconductor.TabIndex = 145
        Me.lblconductor.Text = "CONDUCTOR"
        '
        'dgvPaquetes
        '
        Me.dgvPaquetes.AllowUserToDeleteRows = False
        Me.dgvPaquetes.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.dgvPaquetes.Columns.AddRange(New System.Windows.Forms.DataGridViewColumn() {Me.CODIGO, Me.DESTINARIO, Me.PESO, Me.CONDUCTOR, Me.DIRECCION, Me.PROVINCIA, Me.DETALLE_PAQUETE})
        Me.dgvPaquetes.Location = New System.Drawing.Point(341, 100)
        Me.dgvPaquetes.Margin = New System.Windows.Forms.Padding(4)
        Me.dgvPaquetes.Name = "dgvPaquetes"
        Me.dgvPaquetes.ReadOnly = True
        Me.dgvPaquetes.RowHeadersWidth = 51
        Me.dgvPaquetes.Size = New System.Drawing.Size(927, 247)
        Me.dgvPaquetes.TabIndex = 139
        '
        'CODIGO
        '
        Me.CODIGO.DataPropertyName = "codigo"
        Me.CODIGO.HeaderText = "CODIGO"
        Me.CODIGO.MinimumWidth = 6
        Me.CODIGO.Name = "CODIGO"
        Me.CODIGO.ReadOnly = True
        Me.CODIGO.Width = 125
        '
        'DESTINARIO
        '
        Me.DESTINARIO.DataPropertyName = "destinatario"
        Me.DESTINARIO.HeaderText = "DESTINARIO"
        Me.DESTINARIO.MinimumWidth = 6
        Me.DESTINARIO.Name = "DESTINARIO"
        Me.DESTINARIO.ReadOnly = True
        Me.DESTINARIO.Width = 125
        '
        'PESO
        '
        Me.PESO.DataPropertyName = "peso"
        Me.PESO.HeaderText = "PESO"
        Me.PESO.MinimumWidth = 6
        Me.PESO.Name = "PESO"
        Me.PESO.ReadOnly = True
        Me.PESO.Width = 125
        '
        'CONDUCTOR
        '
        Me.CONDUCTOR.DataPropertyName = "fk_cedula"
        Me.CONDUCTOR.HeaderText = "CONDUCTOR"
        Me.CONDUCTOR.MinimumWidth = 6
        Me.CONDUCTOR.Name = "CONDUCTOR"
        Me.CONDUCTOR.ReadOnly = True
        Me.CONDUCTOR.Width = 125
        '
        'DIRECCION
        '
        Me.DIRECCION.DataPropertyName = "dir_destinatario"
        Me.DIRECCION.HeaderText = "DIRECCION"
        Me.DIRECCION.MinimumWidth = 6
        Me.DIRECCION.Name = "DIRECCION"
        Me.DIRECCION.ReadOnly = True
        Me.DIRECCION.Width = 125
        '
        'PROVINCIA
        '
        Me.PROVINCIA.DataPropertyName = "fk_codigo_prov"
        Me.PROVINCIA.HeaderText = "PROVINCIA"
        Me.PROVINCIA.MinimumWidth = 6
        Me.PROVINCIA.Name = "PROVINCIA"
        Me.PROVINCIA.ReadOnly = True
        Me.PROVINCIA.Width = 125
        '
        'DETALLE_PAQUETE
        '
        Me.DETALLE_PAQUETE.DataPropertyName = "fk_detalle_paquete"
        Me.DETALLE_PAQUETE.HeaderText = "DETALLE_PAQUETE"
        Me.DETALLE_PAQUETE.MinimumWidth = 6
        Me.DETALLE_PAQUETE.Name = "DETALLE_PAQUETE"
        Me.DETALLE_PAQUETE.ReadOnly = True
        Me.DETALLE_PAQUETE.Width = 125
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label2.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label2.Location = New System.Drawing.Point(821, 457)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(54, 21)
        Me.Label2.TabIndex = 174
        Me.Label2.Text = "Cerrar"
        Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label3.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label3.Location = New System.Drawing.Point(619, 457)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(76, 21)
        Me.Label3.TabIndex = 173
        Me.Label3.Text = "Modificar"
        '
        'Label4
        '
        Me.Label4.AutoSize = True
        Me.Label4.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label4.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label4.Location = New System.Drawing.Point(524, 457)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(55, 21)
        Me.Label4.TabIndex = 172
        Me.Label4.Text = "Nuevo"
        '
        'Label5
        '
        Me.Label5.AutoSize = True
        Me.Label5.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label5.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label5.Location = New System.Drawing.Point(725, 457)
        Me.Label5.Name = "Label5"
        Me.Label5.Size = New System.Drawing.Size(65, 21)
        Me.Label5.TabIndex = 171
        Me.Label5.Text = "Eliminar"
        '
        'Label6
        '
        Me.Label6.AutoSize = True
        Me.Label6.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label6.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label6.Location = New System.Drawing.Point(428, 457)
        Me.Label6.Name = "Label6"
        Me.Label6.Size = New System.Drawing.Size(66, 21)
        Me.Label6.TabIndex = 170
        Me.Label6.Text = "Guardar"
        '
        'btnCerrar
        '
        Me.btnCerrar.BackColor = System.Drawing.Color.Gray
        Me.btnCerrar.BackgroundImage = CType(resources.GetObject("btnCerrar.BackgroundImage"), System.Drawing.Image)
        Me.btnCerrar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnCerrar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnCerrar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnCerrar.ForeColor = System.Drawing.Color.Black
        Me.btnCerrar.Location = New System.Drawing.Point(821, 393)
        Me.btnCerrar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnCerrar.Name = "btnCerrar"
        Me.btnCerrar.Size = New System.Drawing.Size(59, 43)
        Me.btnCerrar.TabIndex = 169
        Me.btnCerrar.UseVisualStyleBackColor = False
        '
        'btnEliminar
        '
        Me.btnEliminar.BackColor = System.Drawing.Color.Gray
        Me.btnEliminar.BackgroundImage = CType(resources.GetObject("btnEliminar.BackgroundImage"), System.Drawing.Image)
        Me.btnEliminar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnEliminar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnEliminar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnEliminar.Location = New System.Drawing.Point(725, 393)
        Me.btnEliminar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnEliminar.Name = "btnEliminar"
        Me.btnEliminar.Size = New System.Drawing.Size(59, 43)
        Me.btnEliminar.TabIndex = 168
        Me.btnEliminar.UseVisualStyleBackColor = False
        '
        'btnModificar
        '
        Me.btnModificar.BackColor = System.Drawing.Color.Gray
        Me.btnModificar.BackgroundImage = CType(resources.GetObject("btnModificar.BackgroundImage"), System.Drawing.Image)
        Me.btnModificar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnModificar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnModificar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnModificar.Location = New System.Drawing.Point(619, 393)
        Me.btnModificar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnModificar.Name = "btnModificar"
        Me.btnModificar.Size = New System.Drawing.Size(59, 43)
        Me.btnModificar.TabIndex = 167
        Me.btnModificar.UseVisualStyleBackColor = False
        '
        'btnGuardar
        '
        Me.btnGuardar.BackColor = System.Drawing.Color.Gray
        Me.btnGuardar.BackgroundImage = CType(resources.GetObject("btnGuardar.BackgroundImage"), System.Drawing.Image)
        Me.btnGuardar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnGuardar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnGuardar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnGuardar.Location = New System.Drawing.Point(428, 393)
        Me.btnGuardar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnGuardar.Name = "btnGuardar"
        Me.btnGuardar.Size = New System.Drawing.Size(59, 43)
        Me.btnGuardar.TabIndex = 166
        Me.btnGuardar.UseVisualStyleBackColor = False
        '
        'btnNuevo
        '
        Me.btnNuevo.BackColor = System.Drawing.Color.Gray
        Me.btnNuevo.BackgroundImage = CType(resources.GetObject("btnNuevo.BackgroundImage"), System.Drawing.Image)
        Me.btnNuevo.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnNuevo.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnNuevo.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnNuevo.Location = New System.Drawing.Point(524, 393)
        Me.btnNuevo.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnNuevo.Name = "btnNuevo"
        Me.btnNuevo.Size = New System.Drawing.Size(59, 43)
        Me.btnNuevo.TabIndex = 165
        Me.btnNuevo.UseVisualStyleBackColor = False
        '
        'frmPaquete
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.SystemColors.ActiveBorder
        Me.ClientSize = New System.Drawing.Size(1281, 531)
        Me.Controls.Add(Me.Label2)
        Me.Controls.Add(Me.Label3)
        Me.Controls.Add(Me.Label4)
        Me.Controls.Add(Me.Label5)
        Me.Controls.Add(Me.Label6)
        Me.Controls.Add(Me.btnCerrar)
        Me.Controls.Add(Me.btnEliminar)
        Me.Controls.Add(Me.btnModificar)
        Me.Controls.Add(Me.btnGuardar)
        Me.Controls.Add(Me.btnNuevo)
        Me.Controls.Add(Me.txtDireccion)
        Me.Controls.Add(Me.cmbProvincia)
        Me.Controls.Add(Me.cmbConductor)
        Me.Controls.Add(Me.cmbDetalle)
        Me.Controls.Add(Me.txtPeso)
        Me.Controls.Add(Me.txtDestinatario)
        Me.Controls.Add(Me.txtCodigo)
        Me.Controls.Add(Me.lbldestinatario)
        Me.Controls.Add(Me.lblcedula)
        Me.Controls.Add(Me.lblpeso)
        Me.Controls.Add(Me.lblcodigo)
        Me.Controls.Add(Me.Label1)
        Me.Controls.Add(Me.Lbl_detalle_paquete)
        Me.Controls.Add(Me.Lblprovincia)
        Me.Controls.Add(Me.lblconductor)
        Me.Controls.Add(Me.dgvPaquetes)
        Me.Name = "frmPaquete"
        Me.Text = "frmPaquete"
        CType(Me.dgvPaquetes, System.ComponentModel.ISupportInitialize).EndInit()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents txtDireccion As ComboBox
    Friend WithEvents cmbProvincia As ComboBox
    Friend WithEvents cmbConductor As ComboBox
    Friend WithEvents cmbDetalle As ComboBox
    Friend WithEvents txtPeso As TextBox
    Friend WithEvents txtDestinatario As TextBox
    Friend WithEvents txtCodigo As TextBox
    Friend WithEvents lbldestinatario As Label
    Friend WithEvents lblcedula As Label
    Friend WithEvents lblpeso As Label
    Friend WithEvents lblcodigo As Label
    Friend WithEvents Label1 As Label
    Friend WithEvents Lbl_detalle_paquete As Label
    Friend WithEvents Lblprovincia As Label
    Friend WithEvents lblconductor As Label
    Friend WithEvents dgvPaquetes As DataGridView
    Friend WithEvents CODIGO As DataGridViewTextBoxColumn
    Friend WithEvents DESTINARIO As DataGridViewTextBoxColumn
    Friend WithEvents PESO As DataGridViewTextBoxColumn
    Friend WithEvents CONDUCTOR As DataGridViewTextBoxColumn
    Friend WithEvents DIRECCION As DataGridViewTextBoxColumn
    Friend WithEvents PROVINCIA As DataGridViewTextBoxColumn
    Friend WithEvents DETALLE_PAQUETE As DataGridViewTextBoxColumn
    Friend WithEvents Label2 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents Label6 As Label
    Friend WithEvents btnCerrar As Button
    Friend WithEvents btnEliminar As Button
    Friend WithEvents btnModificar As Button
    Friend WithEvents btnGuardar As Button
    Friend WithEvents btnNuevo As Button
End Class
