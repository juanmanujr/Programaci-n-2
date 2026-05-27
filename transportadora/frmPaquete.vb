Public Class frmPaquete

    Private Sub frmPaquete_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Try
            cargarConductores()
            cargarProvincias()
            cargarDetalles()
            cargar_grilla()
            DESABILITARTXT()
        Catch ex As Exception
            MsgBox("Error al iniciar formulario: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub cargar_grilla()
        Try
            Dim query As String =
                "SELECT p.codigo AS ""codigo"", " &
                "p.destinatario AS ""destinatario"", " &
                "p.peso AS ""peso"", " &
                "p.dir_destinatario AS ""direccion"", " &
                "p.fk_cedula AS ""conductor"", " &
                "c.nombre || ' ' || c.apellido AS ""nombre_conductor"", " &
                "p.fk_codigo_prov AS ""provincia"", " &
                "pr.nombre AS ""nombre_provincia"", " &
                "p.fk_detalle_paquete AS ""detalle_paquete"", " &
                "dp.descripcion AS ""nombre_detalle"" " &
                "FROM paquete p " &
                "INNER JOIN conductor c ON p.fk_cedula = c.cedula " &
                "INNER JOIN provincia pr ON p.fk_codigo_prov = pr.codigo " &
                "INNER JOIN detalle_paquete dp ON p.fk_detalle_paquete = dp.id_detalle"

            Dim dt As DataTable = conexiones.consulta(query)

            dgvPaquetes.AutoGenerateColumns = True
            dgvPaquetes.Columns.Clear()
            dgvPaquetes.DataSource = dt
        Catch ex As Exception
            MsgBox("Error al cargar la grilla: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub


    Private Sub cargarConductores()
        Dim dt As DataTable = conexiones.consulta("SELECT cedula, nombre || ' ' || apellido AS nombre FROM conductor")
        cmbConductor.DataSource = dt
        cmbConductor.DisplayMember = "nombre"
        cmbConductor.ValueMember = "cedula"
        cmbConductor.SelectedIndex = -1
    End Sub

    Private Sub cargarProvincias()
        Dim dt As DataTable = conexiones.consulta("SELECT codigo, nombre FROM provincia")
        cmbProvincia.DataSource = dt
        cmbProvincia.DisplayMember = "nombre"
        cmbProvincia.ValueMember = "codigo"
        cmbProvincia.SelectedIndex = -1
    End Sub

    Private Sub cargarDetalles()
        Dim dt As DataTable = conexiones.consulta("SELECT id_detalle, descripcion FROM detalle_paquete")
        cmbDetalle.DataSource = dt
        cmbDetalle.DisplayMember = "descripcion"
        cmbDetalle.ValueMember = "id_detalle"
        cmbDetalle.SelectedIndex = -1
    End Sub


    Private Sub btnNuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        HABILITARTXT()
        LIMPIARTXT()
        txtDestinatario.Focus()
    End Sub

    Private Sub btnGuardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If txtDestinatario.Text = "" OrElse txtPeso.Text = "" OrElse cmbConductor.SelectedIndex = -1 OrElse cmbProvincia.SelectedIndex = -1 OrElse cmbDetalle.SelectedIndex = -1 Then
            MsgBox("Complete todos los campos", MsgBoxStyle.Exclamation)
        Else
            Dim query As String =
                "INSERT INTO paquete (destinatario, peso, dir_destinatario, fk_cedula, fk_codigo_prov, fk_detalle_paquete) " &
                "VALUES ('" & txtDestinatario.Text & "', " & txtPeso.Text.Replace(",", ".") & ", '" & txtDireccion.Text & "', " &
                "'" & cmbConductor.SelectedValue & "', " & cmbProvincia.SelectedValue & ", " & cmbDetalle.SelectedValue & ")"

            If conexiones.executarsql(query) Then
                MsgBox("Paquete registrado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al registrar el paquete", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btnModificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        If txtCodigo.Text = "" Then
            MsgBox("Seleccione un paquete", MsgBoxStyle.Critical)
        Else
            Dim query As String =
                "UPDATE paquete SET destinatario='" & txtDestinatario.Text & "', " &
                "peso=" & txtPeso.Text.Replace(",", ".") & ", " &
                "dir_destinatario='" & txtDireccion.Text & "', " &
                "fk_cedula='" & cmbConductor.SelectedValue & "', " &
                "fk_codigo_prov=" & cmbProvincia.SelectedValue & ", " &
                "fk_detalle_paquete=" & cmbDetalle.SelectedValue & " " &
                "WHERE codigo=" & txtCodigo.Text

            If conexiones.executarsql(query) Then
                MsgBox("Paquete modificado con éxito", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESABILITARTXT()
            Else
                MsgBox("Error al modificar el paquete", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btnEliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        If txtCodigo.Text <> "" Then
            If MsgBox("¿Está seguro de eliminar este paquete?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
                Dim query As String = "DELETE FROM paquete WHERE codigo=" & txtCodigo.Text
                If conexiones.executarsql(query) Then
                    MsgBox("Paquete eliminado con éxito", MsgBoxStyle.Information)
                    cargar_grilla()
                    LIMPIARTXT()
                    DESABILITARTXT()
                Else
                    MsgBox("Error al eliminar el paquete", MsgBoxStyle.Critical)
                End If
            End If
        Else
            MsgBox("Seleccione un paquete", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnCerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub


    Private Sub dgvPaquetes_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvPaquetes.CellClick
        Try
            If e.RowIndex >= 0 Then
                Dim fila As DataGridViewRow = dgvPaquetes.Rows(e.RowIndex)

                txtCodigo.Text = If(fila.Cells("codigo").Value IsNot Nothing, fila.Cells("codigo").Value.ToString(), "")
                txtDestinatario.Text = If(fila.Cells("destinatario").Value IsNot Nothing, fila.Cells("destinatario").Value.ToString(), "")
                txtPeso.Text = If(fila.Cells("peso").Value IsNot Nothing, fila.Cells("peso").Value.ToString(), "")
                txtDireccion.Text = If(fila.Cells("direccion").Value IsNot Nothing, fila.Cells("direccion").Value.ToString(), "")

                If Not IsDBNull(fila.Cells("conductor").Value) Then cmbConductor.SelectedValue = fila.Cells("conductor").Value
                If Not IsDBNull(fila.Cells("provincia").Value) Then cmbProvincia.SelectedValue = fila.Cells("provincia").Value
                If Not IsDBNull(fila.Cells("detalle_paquete").Value) Then cmbDetalle.SelectedValue = fila.Cells("detalle_paquete").Value

                HABILITARTXT()
            End If
        Catch ex As Exception
            MsgBox("Error al seleccionar el paquete: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Sub HABILITARTXT()
        txtCodigo.Enabled = False
        txtDestinatario.Enabled = True
        txtPeso.Enabled = True
        txtDireccion.Enabled = True
        cmbConductor.Enabled = True
        cmbProvincia.Enabled = True
        cmbDetalle.Enabled = True
    End Sub

    Sub DESABILITARTXT()
        txtCodigo.Enabled = False
        txtDestinatario.Enabled = False
        txtPeso.Enabled = False
        txtDireccion.Enabled = False
        cmbConductor.Enabled = False
        cmbProvincia.Enabled = False
        cmbDetalle.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtCodigo.Text = ""
        txtDestinatario.Text = ""
        txtPeso.Text = ""
        txtDireccion.Text = ""
        cmbConductor.SelectedIndex = -1
        cmbProvincia.SelectedIndex = -1
        cmbDetalle.SelectedIndex = -1
    End Sub

End Class