Public Class frmDetalle_Paquete

    Private Sub frmDetalle_Paquete_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        LIMPIARTXT()
        DESABILITARTXT()
        cargar_grilla()
    End Sub


    Private Sub cargar_grilla()
        Dim query As String =
            "SELECT id_detalle AS ""id_detalle"", " &
            "descripcion AS ""descripcion"", " &
            "precio AS ""precio"" " &
            "FROM detalle_paquete ORDER BY id_detalle"

        Dim dt As DataTable = conexiones.consulta(query)

        dgvDetallePaquete.AutoGenerateColumns = True
        dgvDetallePaquete.Columns.Clear()
        dgvDetallePaquete.DataSource = dt
    End Sub

    Private Sub btnnuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        LIMPIARTXT()
        HABILITARTXT()
        txtDescripcion.Focus()
    End Sub

    Private Sub btnguardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If txtDescripcion.Text.Trim = "" Or txtPrecio.Text.Trim = "" Then
            MsgBox("Complete descripción y precio", MsgBoxStyle.Exclamation)
            Exit Sub
        End If

        If Not IsNumeric(txtPrecio.Text) Then
            MsgBox("El precio debe ser numérico", MsgBoxStyle.Exclamation)
            Exit Sub
        End If

        Dim precioFormatted As String = txtPrecio.Text.Trim.Replace(",", ".")
        Dim query As String =
            "INSERT INTO detalle_paquete (descripcion, precio) " &
            "VALUES ('" & txtDescripcion.Text.Trim & "', " & precioFormatted & ")"

        If conexiones.executarsql(query) Then
            MsgBox("Detalle guardado", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESABILITARTXT()
        Else
            MsgBox("Error al guardar detalle", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnmodificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        If txtId.Text.Trim = "" Then
            MsgBox("Seleccione un detalle para modificar", MsgBoxStyle.Critical)
            Exit Sub
        End If

        If Not IsNumeric(txtPrecio.Text) Then
            MsgBox("El precio debe ser numérico", MsgBoxStyle.Exclamation)
            Exit Sub
        End If

        Dim precioFormatted As String = txtPrecio.Text.Trim.Replace(",", ".")
        Dim query As String =
            "UPDATE detalle_paquete SET descripcion='" & txtDescripcion.Text.Trim & "', " &
            "precio=" & precioFormatted & " WHERE id_detalle=" & txtId.Text.Trim

        If conexiones.executarsql(query) Then
            MsgBox("Detalle modificado", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESABILITARTXT()
        Else
            MsgBox("Error al modificar detalle", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btneliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        If txtId.Text.Trim = "" Then
            MsgBox("Seleccione un detalle para eliminar", MsgBoxStyle.Critical)
            Exit Sub
        End If

        If MsgBox("¿Eliminar este detalle de paquete?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
            Dim query As String = "DELETE FROM detalle_paquete WHERE id_detalle=" & txtId.Text.Trim
            If conexiones.executarsql(query) Then
                MsgBox("Detalle eliminado", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al eliminar detalle", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btncerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub

    Private Sub dgvDetallePaquete_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvDetallePaquete.CellClick
        Try
            If e.RowIndex >= 0 Then
                Dim fila = dgvDetallePaquete.Rows(e.RowIndex)

                txtId.Text = fila.Cells("id_detalle").Value.ToString()
                txtDescripcion.Text = fila.Cells("descripcion").Value.ToString()
                txtPrecio.Text = fila.Cells("precio").Value.ToString()

                HABILITARTXT()
                txtId.Enabled = False
            End If
        Catch ex As Exception
            MsgBox("Error al seleccionar detalle: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub


    Sub HABILITARTXT()
        txtId.Enabled = False
        txtDescripcion.Enabled = True
        txtPrecio.Enabled = True
    End Sub

    Sub DESABILITARTXT()
        txtId.Enabled = False
        txtDescripcion.Enabled = False
        txtPrecio.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtId.Text = ""
        txtDescripcion.Text = ""
        txtPrecio.Text = ""
    End Sub

End Class