Public Class frmClientes
    Private Sub btnGuardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If txtNombre.Text = "" Then
            MsgBox("Cargue el nombre")
        ElseIf txtApellido.Text = "" Then
            MsgBox("Cargue el apellido")
        ElseIf txtDireccion.Text = "" Then
            MsgBox("Cargue la direccion")
        ElseIf txtTelefono.Text = "" Then
            MsgBox("Cargue el telefono")
        ElseIf txtEmail.Text = "" Then
            MsgBox("Cargue el email")
        Else
            Dim query As String = "INSERT INTO clientes ()"
        End If

    End Sub
End Class
