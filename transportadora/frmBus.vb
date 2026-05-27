Public Class frmBus

    Private Sub frmBuses_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        cargarContactos()
        cargar_grilla()
        DESHABILITARTXT()
    End Sub


    Private Sub cargar_grilla()
        Dim query As String =
            "SELECT b.matricula, b.modelo, b.tipo, b.capacidad, " &
            "c.id_contacto, c.telefono, c.email " &
            "FROM Bus b " &
            "INNER JOIN Contacto c ON b.fk_contacto = c.id_contacto"

        Dim dt As DataTable = conexiones.consulta(query)

        dgvBuses.AutoGenerateColumns = True
        dgvBuses.Columns.Clear()
        dgvBuses.DataSource = dt


        If dgvBuses.Columns.Contains("id_contacto") Then
            dgvBuses.Columns("id_contacto").Visible = False
        End If
    End Sub


    Private Sub btnNuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        LIMPIARTXT()
        HABILITARTXT()
        txtMatricula.Focus()
    End Sub

    Private Sub btnGuardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If txtMatricula.Text = "" Or txtModelo.Text = "" Or txtTipo.Text = "" Or txtCapacidad.Text = "" Or cmbContacto.SelectedIndex = -1 Then
            MsgBox("Complete todos los campos", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "INSERT INTO Bus (matricula, modelo, tipo, capacidad, tel_contc, fk_contacto) " &
            "VALUES ('" & txtMatricula.Text & "','" & txtModelo.Text & "','" & txtTipo.Text & "'," &
            txtCapacidad.Text & ",'" & txtTelContacto.Text & "'," & cmbContacto.SelectedValue & ")"

        If conexiones.executarsql(query) Then
            MsgBox("Bus guardado", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESHABILITARTXT()
        Else
            MsgBox("Error al guardar bus", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnModificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        If txtMatricula.Text = "" Then
            MsgBox("Seleccione un bus", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "UPDATE Bus SET modelo='" & txtModelo.Text & "', tipo='" & txtTipo.Text & "', " &
            "capacidad=" & txtCapacidad.Text & ", tel_contc='" & txtTelContacto.Text & "', " &
            "fk_contacto=" & cmbContacto.SelectedValue & " WHERE matricula='" & txtMatricula.Text & "'"

        If conexiones.executarsql(query) Then
            MsgBox("Bus modificado", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESHABILITARTXT()
        Else
            MsgBox("Error al modificar bus", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnEliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        If txtMatricula.Text = "" Then
            MsgBox("Seleccione un bus", MsgBoxStyle.Exclamation)
            Return
        End If

        If MsgBox("¿Está seguro de eliminar el bus?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
            Dim query As String = "DELETE FROM Bus WHERE matricula='" & txtMatricula.Text & "'"
            If conexiones.executarsql(query) Then
                MsgBox("Bus eliminado", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESHABILITARTXT()
            Else
                MsgBox("Error al eliminar bus", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btnCerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub

    Private Sub dgvBuses_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvBuses.CellClick
        Try
            If e.RowIndex >= 0 Then
                Dim fila = dgvBuses.Rows(e.RowIndex)

                txtMatricula.Text = fila.Cells("matricula").Value.ToString()
                txtModelo.Text = fila.Cells("modelo").Value.ToString()
                txtTipo.Text = fila.Cells("tipo").Value.ToString()
                txtCapacidad.Text = fila.Cells("capacidad").Value.ToString()
                txtTelContacto.Text = fila.Cells("telefono").Value.ToString()

                If Not IsDBNull(fila.Cells("id_contacto").Value) Then
                    cmbContacto.SelectedValue = fila.Cells("id_contacto").Value
                End If

                HABILITARTXT()
                txtMatricula.Enabled = False ' no permitir modificar PK
            End If
        Catch ex As Exception
            MsgBox("Error al seleccionar bus: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub


    Private Sub cargarContactos()
        Dim dt As DataTable = conexiones.consulta("SELECT id_contacto, telefono FROM Contacto")
        cmbContacto.DataSource = dt
        cmbContacto.DisplayMember = "telefono"
        cmbContacto.ValueMember = "id_contacto"
        cmbContacto.SelectedIndex = -1
    End Sub

    Sub HABILITARTXT()
        txtMatricula.Enabled = True
        txtModelo.Enabled = True
        txtTipo.Enabled = True
        txtCapacidad.Enabled = True
        txtTelContacto.Enabled = True
        cmbContacto.Enabled = True
    End Sub

    Sub DESHABILITARTXT()
        txtMatricula.Enabled = False
        txtModelo.Enabled = False
        txtTipo.Enabled = False
        txtCapacidad.Enabled = False
        txtTelContacto.Enabled = False
        cmbContacto.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtMatricula.Text = ""
        txtModelo.Text = ""
        txtTipo.Text = ""
        txtCapacidad.Text = ""
        txtTelContacto.Text = ""
        cmbContacto.SelectedIndex = -1
    End Sub

End Class