Public Class frmContacto

    Private Sub frmContactos_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Try
            ' Deshabilita la auto-generación de columnas para que se usen las del diseño.
            dgvContactos.AutoGenerateColumns = False
            cargar_grilla()
            DESABILITARTXT()
        Catch ex As Exception
            MsgBox("Error al iniciar formulario: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub cargar_grilla()
        Try
            Dim dt As DataTable = conexiones.consulta("SELECT * FROM Contacto")
            dgvContactos.DataSource = dt
        Catch ex As Exception
            MsgBox("Error al cargar la grilla: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btnnuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        LIMPIARTXT()
        HABILITARTXT()
        txtTelefono.Focus()
    End Sub

    Private Sub btnguardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        Try
            If txtTelefono.Text.Trim = "" Then
                MsgBox("Complete el campo de teléfono", MsgBoxStyle.Exclamation)
                Exit Sub
            End If

            Dim query As String = "INSERT INTO Contacto (telefono, email, foto_bus) VALUES ('" &
                                 txtTelefono.Text.Trim & "', '" & txtEmail.Text.Trim & "', '" & txtFoto.Text.Trim & "')"
            If conexiones.executarsql(query) Then
                MsgBox("Contacto guardado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al guardar el contacto", MsgBoxStyle.Critical)
            End If
        Catch ex As Exception
            MsgBox("Error al guardar: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btnmodificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        Try
            If txtId.Text.Trim = "" Or txtTelefono.Text.Trim = "" Then
                MsgBox("Seleccione un contacto y complete el campo de teléfono", MsgBoxStyle.Exclamation)
                Exit Sub
            End If

            Dim query As String = "UPDATE Contacto SET telefono='" & txtTelefono.Text.Trim & "', email='" & txtEmail.Text.Trim &
                                 "', foto_bus='" & txtFoto.Text.Trim & "' WHERE id_contacto=" & txtId.Text.Trim
            If conexiones.executarsql(query) Then
                MsgBox("Contacto modificado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al modificar el contacto", MsgBoxStyle.Critical)
            End If
        Catch ex As Exception
            MsgBox("Error al modificar: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub btneliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        Try
            If txtId.Text.Trim = "" Then
                MsgBox("Seleccione un contacto para eliminar", MsgBoxStyle.Exclamation)
                Exit Sub
            End If

            If MsgBox("¿Está seguro de eliminar este contacto?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
                Dim query As String = "DELETE FROM Contacto WHERE id_contacto=" & txtId.Text.Trim
                If conexiones.executarsql(query) Then
                    MsgBox("Contacto eliminado con éxito", MsgBoxStyle.Information)
                    cargar_grilla()
                    LIMPIARTXT()
                    DESABILITARTXT()
                Else
                    MsgBox("Error al eliminar el contacto (revise dependencias)", MsgBoxStyle.Critical)
                End If
            End If
        Catch ex As Exception
            MsgBox("Error al eliminar: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub dgvContactos_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvContactos.CellClick
        If e.RowIndex >= 0 Then
            Try
                Dim fila As DataGridViewRow = dgvContactos.Rows(e.RowIndex)


                txtId.Text = fila.Cells("ID").Value.ToString()
                txtTelefono.Text = fila.Cells("TELEFONO").Value.ToString()
                txtEmail.Text = fila.Cells("EMAIL").Value.ToString()
                txtFoto.Text = fila.Cells("FOTO_BUS").Value.ToString()

                HABILITARTXT()
            Catch ex As Exception
                MsgBox("Error al seleccionar la fila: " & ex.Message, MsgBoxStyle.Critical)
            End Try
        End If
    End Sub

    Private Sub btncerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub

    Sub HABILITARTXT()
        txtId.Enabled = False
        txtTelefono.Enabled = True
        txtEmail.Enabled = True
        txtFoto.Enabled = True
    End Sub

    Sub DESABILITARTXT()
        txtId.Enabled = False
        txtTelefono.Enabled = False
        txtEmail.Enabled = False
        txtFoto.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtId.Text = ""
        txtTelefono.Text = ""
        txtEmail.Text = ""
        txtFoto.Text = ""
    End Sub

End Class