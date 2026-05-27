Public Class frmProvincia

    Private Sub frmProvincia_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        cargar_grilla()
        DESABILITARTXT()
    End Sub


    Private Sub cargar_grilla()
        Dim query As String = "SELECT codigo AS ""codigo"", nombre AS ""nombre"" FROM Provincia"
        Dim dt As DataTable = conexiones.consulta(query)

        dgvProvincias.AutoGenerateColumns = True
        dgvProvincias.Columns.Clear()
        dgvProvincias.DataSource = dt
    End Sub

    Private Sub btnnuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        LIMPIARTXT()
        HABILITARTXT()
        txtCodigo.Focus()
    End Sub

    Private Sub btnguardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If txtCodigo.Text = "" Or txtNombre.Text = "" Then
            MsgBox("Complete todos los campos", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "INSERT INTO Provincia (codigo, nombre) VALUES (" & txtCodigo.Text & ",'" & txtNombre.Text & "')"

        If conexiones.executarsql(query) Then
            cargar_grilla()
            MsgBox("Provincia guardada", MsgBoxStyle.Information)
            LIMPIARTXT()
            DESABILITARTXT()
        Else
            MsgBox("Error al guardar provincia", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnmodificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        If txtCodigo.Text = "" Then
            MsgBox("Seleccione una provincia", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "UPDATE Provincia SET nombre='" & txtNombre.Text & "' WHERE codigo=" & txtCodigo.Text

        If conexiones.executarsql(query) Then
            cargar_grilla()
            MsgBox("Provincia modificada", MsgBoxStyle.Information)
            LIMPIARTXT()
            DESABILITARTXT()
        Else
            MsgBox("Error al modificar provincia", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btneliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        If txtCodigo.Text = "" Then
            MsgBox("Seleccione una provincia", MsgBoxStyle.Exclamation)
            Return
        End If

        If MsgBox("¿Está seguro de eliminar la provincia?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
            Dim query As String = "DELETE FROM Provincia WHERE codigo=" & txtCodigo.Text
            If conexiones.executarsql(query) Then
                cargar_grilla()
                MsgBox("Provincia eliminada", MsgBoxStyle.Information)
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al eliminar provincia", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btncerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub


    Private Sub dgvProvincias_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvProvincias.CellClick
        Try
            If e.RowIndex >= 0 Then
                Dim fila = dgvProvincias.Rows(e.RowIndex)

                txtCodigo.Text = fila.Cells("codigo").Value.ToString()
                txtNombre.Text = fila.Cells("nombre").Value.ToString()

                HABILITARTXT()
                txtCodigo.Enabled = False ' PK no editable
            End If
        Catch ex As Exception
            MsgBox("Error al seleccionar provincia: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub


    Sub HABILITARTXT()
        txtCodigo.Enabled = True
        txtNombre.Enabled = True
    End Sub

    Sub DESABILITARTXT()
        txtCodigo.Enabled = False
        txtNombre.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtCodigo.Text = ""
        txtNombre.Text = ""
    End Sub

End Class