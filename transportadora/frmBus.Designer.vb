<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class frmBus
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(frmBus))
        Me.txtModelo = New System.Windows.Forms.TextBox()
        Me.txtTelContacto = New System.Windows.Forms.TextBox()
        Me.txtTipo = New System.Windows.Forms.TextBox()
        Me.txtCapacidad = New System.Windows.Forms.TextBox()
        Me.txtMatricula = New System.Windows.Forms.TextBox()
        Me.lblmodelo = New System.Windows.Forms.Label()
        Me.lbltelcontc = New System.Windows.Forms.Label()
        Me.lblmatricula = New System.Windows.Forms.Label()
        Me.lblcontacto = New System.Windows.Forms.Label()
        Me.cmbContacto = New System.Windows.Forms.ComboBox()
        Me.lblcapacidad = New System.Windows.Forms.Label()
        Me.dgvBuses = New System.Windows.Forms.DataGridView()
        Me.id_producto = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.MODELO = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.stock_producto = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.precio_producto = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.descripcion_producto = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.nombre_laboratorio = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.lbltipo = New System.Windows.Forms.Label()
        Me.Label1 = New System.Windows.Forms.Label()
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
        CType(Me.dgvBuses, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.SuspendLayout()
        '
        'txtModelo
        '
        Me.txtModelo.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtModelo.Location = New System.Drawing.Point(195, 97)
        Me.txtModelo.Margin = New System.Windows.Forms.Padding(4)
        Me.txtModelo.Name = "txtModelo"
        Me.txtModelo.Size = New System.Drawing.Size(160, 25)
        Me.txtModelo.TabIndex = 110
        '
        'txtTelContacto
        '
        Me.txtTelContacto.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtTelContacto.Location = New System.Drawing.Point(195, 218)
        Me.txtTelContacto.Margin = New System.Windows.Forms.Padding(4)
        Me.txtTelContacto.Name = "txtTelContacto"
        Me.txtTelContacto.Size = New System.Drawing.Size(160, 25)
        Me.txtTelContacto.TabIndex = 109
        '
        'txtTipo
        '
        Me.txtTipo.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtTipo.Location = New System.Drawing.Point(195, 135)
        Me.txtTipo.Margin = New System.Windows.Forms.Padding(4)
        Me.txtTipo.Name = "txtTipo"
        Me.txtTipo.Size = New System.Drawing.Size(160, 25)
        Me.txtTipo.TabIndex = 108
        '
        'txtCapacidad
        '
        Me.txtCapacidad.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtCapacidad.Location = New System.Drawing.Point(195, 177)
        Me.txtCapacidad.Margin = New System.Windows.Forms.Padding(4)
        Me.txtCapacidad.Name = "txtCapacidad"
        Me.txtCapacidad.Size = New System.Drawing.Size(160, 25)
        Me.txtCapacidad.TabIndex = 107
        '
        'txtMatricula
        '
        Me.txtMatricula.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtMatricula.Location = New System.Drawing.Point(195, 52)
        Me.txtMatricula.Margin = New System.Windows.Forms.Padding(4)
        Me.txtMatricula.Name = "txtMatricula"
        Me.txtMatricula.Size = New System.Drawing.Size(160, 25)
        Me.txtMatricula.TabIndex = 106
        '
        'lblmodelo
        '
        Me.lblmodelo.AutoSize = True
        Me.lblmodelo.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblmodelo.Location = New System.Drawing.Point(51, 102)
        Me.lblmodelo.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblmodelo.Name = "lblmodelo"
        Me.lblmodelo.Size = New System.Drawing.Size(68, 19)
        Me.lblmodelo.TabIndex = 105
        Me.lblmodelo.Text = "MODELO"
        '
        'lbltelcontc
        '
        Me.lbltelcontc.AutoSize = True
        Me.lbltelcontc.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lbltelcontc.Location = New System.Drawing.Point(51, 218)
        Me.lbltelcontc.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lbltelcontc.Name = "lbltelcontc"
        Me.lbltelcontc.Size = New System.Drawing.Size(112, 19)
        Me.lbltelcontc.TabIndex = 104
        Me.lbltelcontc.Text = "TEL_CONTACTO"
        '
        'lblmatricula
        '
        Me.lblmatricula.AutoSize = True
        Me.lblmatricula.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblmatricula.Location = New System.Drawing.Point(51, 57)
        Me.lblmatricula.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblmatricula.Name = "lblmatricula"
        Me.lblmatricula.Size = New System.Drawing.Size(88, 19)
        Me.lblmatricula.TabIndex = 102
        Me.lblmatricula.Text = "MATRÍCULA"
        '
        'lblcontacto
        '
        Me.lblcontacto.AutoSize = True
        Me.lblcontacto.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblcontacto.Location = New System.Drawing.Point(51, 257)
        Me.lblcontacto.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblcontacto.Name = "lblcontacto"
        Me.lblcontacto.Size = New System.Drawing.Size(84, 19)
        Me.lblcontacto.TabIndex = 119
        Me.lblcontacto.Text = "CONTACTO"
        '
        'cmbContacto
        '
        Me.cmbContacto.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.cmbContacto.FormattingEnabled = True
        Me.cmbContacto.Location = New System.Drawing.Point(195, 257)
        Me.cmbContacto.Margin = New System.Windows.Forms.Padding(4)
        Me.cmbContacto.Name = "cmbContacto"
        Me.cmbContacto.Size = New System.Drawing.Size(160, 25)
        Me.cmbContacto.TabIndex = 118
        '
        'lblcapacidad
        '
        Me.lblcapacidad.AutoSize = True
        Me.lblcapacidad.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblcapacidad.Location = New System.Drawing.Point(51, 177)
        Me.lblcapacidad.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lblcapacidad.Name = "lblcapacidad"
        Me.lblcapacidad.Size = New System.Drawing.Size(89, 19)
        Me.lblcapacidad.TabIndex = 117
        Me.lblcapacidad.Text = "CAPACIDAD"
        '
        'dgvBuses
        '
        Me.dgvBuses.AllowUserToDeleteRows = False
        Me.dgvBuses.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.dgvBuses.Columns.AddRange(New System.Windows.Forms.DataGridViewColumn() {Me.id_producto, Me.MODELO, Me.stock_producto, Me.precio_producto, Me.descripcion_producto, Me.nombre_laboratorio})
        Me.dgvBuses.Location = New System.Drawing.Point(433, 57)
        Me.dgvBuses.Margin = New System.Windows.Forms.Padding(4)
        Me.dgvBuses.Name = "dgvBuses"
        Me.dgvBuses.ReadOnly = True
        Me.dgvBuses.RowHeadersWidth = 51
        Me.dgvBuses.Size = New System.Drawing.Size(796, 228)
        Me.dgvBuses.TabIndex = 111
        '
        'id_producto
        '
        Me.id_producto.DataPropertyName = "matricula"
        Me.id_producto.HeaderText = "MATRICULA"
        Me.id_producto.MinimumWidth = 6
        Me.id_producto.Name = "id_producto"
        Me.id_producto.ReadOnly = True
        Me.id_producto.Width = 125
        '
        'MODELO
        '
        Me.MODELO.DataPropertyName = "modelo"
        Me.MODELO.HeaderText = "MODELO"
        Me.MODELO.MinimumWidth = 6
        Me.MODELO.Name = "MODELO"
        Me.MODELO.ReadOnly = True
        Me.MODELO.Width = 125
        '
        'stock_producto
        '
        Me.stock_producto.DataPropertyName = "tipo"
        Me.stock_producto.HeaderText = "TIPO"
        Me.stock_producto.MinimumWidth = 6
        Me.stock_producto.Name = "stock_producto"
        Me.stock_producto.ReadOnly = True
        Me.stock_producto.Width = 125
        '
        'precio_producto
        '
        Me.precio_producto.DataPropertyName = "capacidad"
        Me.precio_producto.HeaderText = "CAPACIDAD"
        Me.precio_producto.MinimumWidth = 6
        Me.precio_producto.Name = "precio_producto"
        Me.precio_producto.ReadOnly = True
        Me.precio_producto.Width = 125
        '
        'descripcion_producto
        '
        Me.descripcion_producto.DataPropertyName = "tel_contc"
        Me.descripcion_producto.HeaderText = "TEL_CONTC"
        Me.descripcion_producto.MinimumWidth = 6
        Me.descripcion_producto.Name = "descripcion_producto"
        Me.descripcion_producto.ReadOnly = True
        Me.descripcion_producto.Width = 125
        '
        'nombre_laboratorio
        '
        Me.nombre_laboratorio.DataPropertyName = "fk_contacto"
        Me.nombre_laboratorio.HeaderText = "CONTACTO"
        Me.nombre_laboratorio.MinimumWidth = 6
        Me.nombre_laboratorio.Name = "nombre_laboratorio"
        Me.nombre_laboratorio.ReadOnly = True
        Me.nombre_laboratorio.Width = 125
        '
        'lbltipo
        '
        Me.lbltipo.AutoSize = True
        Me.lbltipo.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lbltipo.Location = New System.Drawing.Point(51, 140)
        Me.lbltipo.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.lbltipo.Name = "lbltipo"
        Me.lbltipo.Size = New System.Drawing.Size(41, 19)
        Me.lbltipo.TabIndex = 103
        Me.lbltipo.Text = "TIPO"
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Font = New System.Drawing.Font("Segoe UI", 16.2!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label1.Location = New System.Drawing.Point(703, 9)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(102, 38)
        Me.Label1.TabIndex = 101
        Me.Label1.Text = "BUSES"
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label2.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label2.Location = New System.Drawing.Point(842, 391)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(54, 21)
        Me.Label2.TabIndex = 164
        Me.Label2.Text = "Cerrar"
        Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label3.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label3.Location = New System.Drawing.Point(640, 391)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(76, 21)
        Me.Label3.TabIndex = 163
        Me.Label3.Text = "Modificar"
        '
        'Label4
        '
        Me.Label4.AutoSize = True
        Me.Label4.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label4.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label4.Location = New System.Drawing.Point(545, 391)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(55, 21)
        Me.Label4.TabIndex = 162
        Me.Label4.Text = "Nuevo"
        '
        'Label5
        '
        Me.Label5.AutoSize = True
        Me.Label5.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label5.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label5.Location = New System.Drawing.Point(746, 391)
        Me.Label5.Name = "Label5"
        Me.Label5.Size = New System.Drawing.Size(65, 21)
        Me.Label5.TabIndex = 161
        Me.Label5.Text = "Eliminar"
        '
        'Label6
        '
        Me.Label6.AutoSize = True
        Me.Label6.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.Label6.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label6.Location = New System.Drawing.Point(449, 391)
        Me.Label6.Name = "Label6"
        Me.Label6.Size = New System.Drawing.Size(66, 21)
        Me.Label6.TabIndex = 160
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
        Me.btnCerrar.Location = New System.Drawing.Point(842, 327)
        Me.btnCerrar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnCerrar.Name = "btnCerrar"
        Me.btnCerrar.Size = New System.Drawing.Size(59, 43)
        Me.btnCerrar.TabIndex = 159
        Me.btnCerrar.UseVisualStyleBackColor = False
        '
        'btnEliminar
        '
        Me.btnEliminar.BackColor = System.Drawing.Color.Gray
        Me.btnEliminar.BackgroundImage = CType(resources.GetObject("btnEliminar.BackgroundImage"), System.Drawing.Image)
        Me.btnEliminar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnEliminar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnEliminar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnEliminar.Location = New System.Drawing.Point(746, 327)
        Me.btnEliminar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnEliminar.Name = "btnEliminar"
        Me.btnEliminar.Size = New System.Drawing.Size(59, 43)
        Me.btnEliminar.TabIndex = 158
        Me.btnEliminar.UseVisualStyleBackColor = False
        '
        'btnModificar
        '
        Me.btnModificar.BackColor = System.Drawing.Color.Gray
        Me.btnModificar.BackgroundImage = CType(resources.GetObject("btnModificar.BackgroundImage"), System.Drawing.Image)
        Me.btnModificar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnModificar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnModificar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnModificar.Location = New System.Drawing.Point(640, 327)
        Me.btnModificar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnModificar.Name = "btnModificar"
        Me.btnModificar.Size = New System.Drawing.Size(59, 43)
        Me.btnModificar.TabIndex = 157
        Me.btnModificar.UseVisualStyleBackColor = False
        '
        'btnGuardar
        '
        Me.btnGuardar.BackColor = System.Drawing.Color.Gray
        Me.btnGuardar.BackgroundImage = CType(resources.GetObject("btnGuardar.BackgroundImage"), System.Drawing.Image)
        Me.btnGuardar.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnGuardar.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnGuardar.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnGuardar.Location = New System.Drawing.Point(449, 327)
        Me.btnGuardar.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnGuardar.Name = "btnGuardar"
        Me.btnGuardar.Size = New System.Drawing.Size(59, 43)
        Me.btnGuardar.TabIndex = 156
        Me.btnGuardar.UseVisualStyleBackColor = False
        '
        'btnNuevo
        '
        Me.btnNuevo.BackColor = System.Drawing.Color.Gray
        Me.btnNuevo.BackgroundImage = CType(resources.GetObject("btnNuevo.BackgroundImage"), System.Drawing.Image)
        Me.btnNuevo.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
        Me.btnNuevo.Cursor = System.Windows.Forms.Cursors.Hand
        Me.btnNuevo.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnNuevo.Location = New System.Drawing.Point(545, 327)
        Me.btnNuevo.Margin = New System.Windows.Forms.Padding(3, 5, 3, 5)
        Me.btnNuevo.Name = "btnNuevo"
        Me.btnNuevo.Size = New System.Drawing.Size(59, 43)
        Me.btnNuevo.TabIndex = 155
        Me.btnNuevo.UseVisualStyleBackColor = False
        '
        'frmBus
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.SystemColors.ActiveBorder
        Me.ClientSize = New System.Drawing.Size(1352, 442)
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
        Me.Controls.Add(Me.txtModelo)
        Me.Controls.Add(Me.txtTelContacto)
        Me.Controls.Add(Me.txtTipo)
        Me.Controls.Add(Me.txtCapacidad)
        Me.Controls.Add(Me.txtMatricula)
        Me.Controls.Add(Me.lblmodelo)
        Me.Controls.Add(Me.lbltelcontc)
        Me.Controls.Add(Me.lblmatricula)
        Me.Controls.Add(Me.lblcontacto)
        Me.Controls.Add(Me.cmbContacto)
        Me.Controls.Add(Me.lblcapacidad)
        Me.Controls.Add(Me.dgvBuses)
        Me.Controls.Add(Me.lbltipo)
        Me.Controls.Add(Me.Label1)
        Me.Name = "frmBus"
        Me.Text = "frmBus"
        CType(Me.dgvBuses, System.ComponentModel.ISupportInitialize).EndInit()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents txtModelo As TextBox
    Friend WithEvents txtTelContacto As TextBox
    Friend WithEvents txtTipo As TextBox
    Friend WithEvents txtCapacidad As TextBox
    Friend WithEvents txtMatricula As TextBox
    Friend WithEvents lblmodelo As Label
    Friend WithEvents lbltelcontc As Label
    Friend WithEvents lblmatricula As Label
    Friend WithEvents lblcontacto As Label
    Friend WithEvents cmbContacto As ComboBox
    Friend WithEvents lblcapacidad As Label
    Friend WithEvents dgvBuses As DataGridView
    Friend WithEvents id_producto As DataGridViewTextBoxColumn
    Friend WithEvents MODELO As DataGridViewTextBoxColumn
    Friend WithEvents stock_producto As DataGridViewTextBoxColumn
    Friend WithEvents precio_producto As DataGridViewTextBoxColumn
    Friend WithEvents descripcion_producto As DataGridViewTextBoxColumn
    Friend WithEvents nombre_laboratorio As DataGridViewTextBoxColumn
    Friend WithEvents lbltipo As Label
    Friend WithEvents Label1 As Label
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
