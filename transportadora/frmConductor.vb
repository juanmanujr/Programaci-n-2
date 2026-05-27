Public Class frmConductor

    Private Sub frmConductor_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Try
            cargarDirecciones()
            cargar_grilla()
            DESABILITARTXT()
        Catch ex As Exception
            MsgBox("Error al iniciar formulario: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub cargar_grilla()
        Try
            Dim query As String =
                "SELECT c.cedula AS cedula, " &
                "c.nombre AS nombre, " &
                "c.apellido AS apellido, " &
                "c.celular AS celular, " &
                "c.salario AS salario, " &
                "c.fk_direccion AS fk_direccion, " &
                "d.direccion AS direccion " &
                "FROM Conductor c " &
                "LEFT JOIN Direccion d ON c.fk_direccion = d.id_direccion " &
                "ORDER BY c.nombre, c.apellido"

            Dim dt As DataTable = conexiones.consulta(query)
            dgvConductores.AutoGenerateColumns = True
            dgvConductores.DataSource = dt
        Catch ex As Exception
            MsgBox("Error al cargar la grilla: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btnnuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        HABILITARTXT()
        LIMPIARTXT()
        txtCedula.Focus()
    End Sub

    Private Sub btnguardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        Try
            If txtCedula.Text.Trim = "" Or txtNombre.Text.Trim = "" Or txtApellido.Text.Trim = "" Then
                MsgBox("Complete todos los campos obligatorios", MsgBoxStyle.Exclamation)
                Exit Sub
            End If

            Dim salarioVal As String = "NULL"
            If txtSalario.Text.Trim <> "" Then
                If Not IsNumeric(txtSalario.Text) Then
                    MsgBox("El salario debe ser numérico", MsgBoxStyle.Exclamation)
                    Exit Sub
                End If
                salarioVal = txtSalario.Text.Trim.Replace(",", ".")
            End If

            Dim fkDir As String = "NULL"
            If cmbDireccion.SelectedIndex <> -1 Then
                fkDir = cmbDireccion.SelectedValue.ToString()
            End If

            Dim query As String =
                "INSERT INTO Conductor (cedula, nombre, apellido, celular, salario, fk_direccion) " &
                "VALUES ('" & txtCedula.Text.Trim & "', '" & txtNombre.Text.Trim & "', '" & txtApellido.Text.Trim & "', '" &
                txtCelular.Text.Trim & "', " & salarioVal & ", " & fkDir & ")"

            If conexiones.executarsql(query) Then
                MsgBox("Conductor guardado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al guardar el conductor", MsgBoxStyle.Critical)
            End If
        Catch ex As Exception
            MsgBox("Error al guardar: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btnmodificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        Try
            If txtCedula.Text.Trim = "" Then
                MsgBox("Seleccione un conductor", MsgBoxStyle.Critical)
                Exit Sub
            End If

            Dim salarioVal As String = "NULL"
            If txtSalario.Text.Trim <> "" Then
                If Not IsNumeric(txtSalario.Text) Then
                    MsgBox("El salario debe ser numérico", MsgBoxStyle.Exclamation)
                    Exit Sub
                End If
                salarioVal = txtSalario.Text.Trim.Replace(",", ".")
            End If

            Dim fkDir As String = "NULL"
            If cmbDireccion.SelectedIndex <> -1 Then
                fkDir = cmbDireccion.SelectedValue.ToString()
            End If

            Dim query As String =
                "UPDATE Conductor SET nombre='" & txtNombre.Text.Trim & "', apellido='" & txtApellido.Text.Trim & "', " &
                "celular='" & txtCelular.Text.Trim & "', salario=" & salarioVal & ", fk_direccion=" & fkDir &
                " WHERE cedula='" & txtCedula.Text.Trim & "'"

            If conexiones.executarsql(query) Then
                MsgBox("Conductor modificado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al modificar el conductor", MsgBoxStyle.Critical)
            End If
        Catch ex As Exception
            MsgBox("Error al modificar: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btneliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        Try
            If txtCedula.Text.Trim = "" Then
                MsgBox("Seleccione un conductor", MsgBoxStyle.Critical)
                Exit Sub
            End If

            If MsgBox("¿Está seguro de eliminar este conductor?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
                Dim query As String = "DELETE FROM Conductor WHERE cedula='" & txtCedula.Text.Trim & "'"
                If conexiones.executarsql(query) Then
                    MsgBox("Conductor eliminado con éxito", MsgBoxStyle.Information)
                    cargar_grilla()
                    LIMPIARTXT()
                    DESABILITARTXT()
                Else
                    MsgBox("Error al eliminar el conductor (revise dependencias)", MsgBoxStyle.Critical)
                End If
            End If
        Catch ex As Exception
            MsgBox("Error al eliminar: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btncerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub

    Private Sub dgvConductores_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvConductores.CellClick
        Try
            If e.RowIndex < 0 Then Return
            Dim fila As DataGridViewRow = dgvConductores.Rows(e.RowIndex)

            If dgvConductores.Columns.Contains("cedula") AndAlso Not IsDBNull(fila.Cells("cedula").Value) Then
                txtCedula.Text = fila.Cells("cedula").Value.ToString()
            Else
                txtCedula.Text = ""
            End If

            If dgvConductores.Columns.Contains("nombre") AndAlso Not IsDBNull(fila.Cells("nombre").Value) Then
                txtNombre.Text = fila.Cells("nombre").Value.ToString()
            Else
                txtNombre.Text = ""
            End If

            If dgvConductores.Columns.Contains("apellido") AndAlso Not IsDBNull(fila.Cells("apellido").Value) Then
                txtApellido.Text = fila.Cells("apellido").Value.ToString()
            Else
                txtApellido.Text = ""
            End If

            If dgvConductores.Columns.Contains("celular") AndAlso Not IsDBNull(fila.Cells("celular").Value) Then
                txtCelular.Text = fila.Cells("celular").Value.ToString()
            Else
                txtCelular.Text = ""
            End If

            If dgvConductores.Columns.Contains("salario") AndAlso Not IsDBNull(fila.Cells("salario").Value) Then
                txtSalario.Text = fila.Cells("salario").Value.ToString()
            Else
                txtSalario.Text = ""
            End If

            If dgvConductores.Columns.Contains("fk_direccion") AndAlso Not IsDBNull(fila.Cells("fk_direccion").Value) Then
                Try
                    cmbDireccion.SelectedValue = Convert.ToInt32(fila.Cells("fk_direccion").Value)
                Catch ex As Exception
                    cmbDireccion.SelectedIndex = -1
                End Try
            Else
                cmbDireccion.SelectedIndex = -1
            End If

            HABILITARTXT()
        Catch ex As Exception
            MsgBox("Error al seleccionar el conductor: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Sub cargarDirecciones()
        Try
            Dim dt As DataTable = conexiones.consulta("SELECT id_direccion, direccion FROM Direccion ORDER BY id_direccion")
            cmbDireccion.DataSource = dt
            cmbDireccion.DisplayMember = "direccion"
            cmbDireccion.ValueMember = "id_direccion"
            cmbDireccion.SelectedIndex = -1
        Catch ex As Exception
            MsgBox("Error al cargar direcciones: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Sub HABILITARTXT()
        txtCedula.Enabled = True
        txtNombre.Enabled = True
        txtApellido.Enabled = True
        txtCelular.Enabled = True
        txtSalario.Enabled = True
        cmbDireccion.Enabled = True
    End Sub

    Sub DESABILITARTXT()
        txtCedula.Enabled = False
        txtNombre.Enabled = False
        txtApellido.Enabled = False
        txtCelular.Enabled = False
        txtSalario.Enabled = False
        cmbDireccion.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtCedula.Text = ""
        txtNombre.Text = ""
        txtApellido.Text = ""
        txtCelular.Text = ""
        txtSalario.Text = ""
        cmbDireccion.SelectedIndex = -1
    End Sub

End Class