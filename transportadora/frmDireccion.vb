Public Class frmDireccion

    Private Sub frmDireccion_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        cargar_grilla()
        DESABILITARTXT()
    End Sub


    Private Sub cargar_grilla()
        Dim query As String = "SELECT * FROM Direccion ORDER BY id_direccion"
        Dim dt As DataTable = conexiones.consulta(query)

        dgvdirecciones.AutoGenerateColumns = False

        dgvdirecciones.DataSource = dt
    End Sub


    Private Sub btnnuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        HABILITARTXT()
        LIMPIARTXT()
        txtdireccion.Focus()
    End Sub

    Private Sub btnguardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If txtcelular.Text.Trim = "" Or txtdireccion.Text.Trim = "" Or txtciudad.Text.Trim = "" Then
            MsgBox("Complete al menos celular, dirección y ciudad", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "INSERT INTO Direccion (celular, direccion, corregimiento, ciudad, distrito, telefono) " &
            "VALUES ('" & txtcelular.Text & "','" & txtdireccion.Text & "','" & txtcorregimiento.Text & "','" &
            txtciudad.Text & "','" & txtdistrito.Text & "','" & txttelefono.Text & "')"

        If conexiones.executarsql(query) Then
            MsgBox("Registro guardado con éxito", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESABILITARTXT()
        Else
            MsgBox("Error al guardar dirección", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnmodificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        If txtid.Text.Trim = "" Then
            MsgBox("Seleccione una dirección para modificar", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "UPDATE Direccion SET celular='" & txtcelular.Text & "', " &
            "direccion='" & txtdireccion.Text & "', " &
            "corregimiento='" & txtcorregimiento.Text & "', " &
            "ciudad='" & txtciudad.Text & "', " &
            "distrito='" & txtdistrito.Text & "', " &
            "telefono='" & txttelefono.Text & "' " &
            "WHERE id_direccion=" & txtid.Text

        If conexiones.executarsql(query) Then
            MsgBox("Registro modificado con éxito", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESABILITARTXT()
        Else
            MsgBox("Error al modificar dirección", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btneliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        If txtid.Text.Trim = "" Then
            MsgBox("Seleccione una dirección para eliminar", MsgBoxStyle.Exclamation)
            Return
        End If

        If MsgBox("¿Eliminar dirección?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
            Dim query As String = "DELETE FROM Direccion WHERE id_direccion=" & txtid.Text
            If conexiones.executarsql(query) Then
                MsgBox("Registro eliminado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al eliminar dirección", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btncerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub

    Private Sub dgvDirecciones_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvdirecciones.CellClick
        Try
            If e.RowIndex >= 0 Then
                Dim fila = dgvdirecciones.Rows(e.RowIndex)

                txtid.Text = fila.Cells("id_direccion").Value.ToString()
                txtcelular.Text = fila.Cells("celular").Value.ToString()
                txtdireccion.Text = fila.Cells("direccion").Value.ToString()
                txtcorregimiento.Text = fila.Cells("corregimiento").Value.ToString()
                txtciudad.Text = fila.Cells("ciudad").Value.ToString()
                txtdistrito.Text = fila.Cells("distrito").Value.ToString()
                txttelefono.Text = fila.Cells("telefono").Value.ToString()

                HABILITARTXT()
                txtid.Enabled = False
            End If
        Catch ex As Exception
            MsgBox("Error al seleccionar dirección: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub


    Sub HABILITARTXT()
        txtid.Enabled = False
        txtcelular.Enabled = True
        txtdireccion.Enabled = True
        txtcorregimiento.Enabled = True
        txtciudad.Enabled = True
        txtdistrito.Enabled = True
        txttelefono.Enabled = True
    End Sub

    Sub DESABILITARTXT()
        txtid.Enabled = False
        txtcelular.Enabled = False
        txtdireccion.Enabled = False
        txtcorregimiento.Enabled = False
        txtciudad.Enabled = False
        txtdistrito.Enabled = False
        txttelefono.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtid.Text = ""
        txtcelular.Text = ""
        txtdireccion.Text = ""
        txtcorregimiento.Text = ""
        txtciudad.Text = ""
        txtdistrito.Text = ""
        txttelefono.Text = ""
    End Sub
End Class