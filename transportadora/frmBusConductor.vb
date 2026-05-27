Public Class frmBusConductor

    Private Sub frmBusConductor_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        cargarBuses()
        cargarConductores()
        cargar_grilla()
        DESHABILITARTXT()
    End Sub


    Private Sub cargar_grilla()
        Dim query As String =
            "SELECT bc.id_bus_conductor, " &
            "b.matricula, " &
            "c.cedula AS cedula_conductor, " &
            "c.nombre || ' ' || c.apellido AS nombre_conductor " &
            "FROM bus_conductor bc " &
            "INNER JOIN bus b ON bc.fk_matricula_bus = b.matricula " &
            "INNER JOIN conductor c ON bc.fk_cedula_conductor = c.cedula"

        Dim dt As DataTable = conexiones.consulta(query)

        dgvBusConductor.AutoGenerateColumns = True
        dgvBusConductor.Columns.Clear()
        dgvBusConductor.DataSource = dt
    End Sub


    Private Sub btnNuevo_Click(sender As Object, e As EventArgs) Handles btnNuevo.Click
        LIMPIARTXT()
        HABILITARTXT()
    End Sub

    Private Sub btnGuardar_Click(sender As Object, e As EventArgs) Handles btnGuardar.Click
        If cmbBus.SelectedIndex = -1 Or cmbConductor.SelectedIndex = -1 Then
            MsgBox("Seleccione un bus y un conductor", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "INSERT INTO bus_conductor (fk_matricula_bus, fk_cedula_conductor) " &
            "VALUES ('" & cmbBus.SelectedValue & "', '" & cmbConductor.SelectedValue & "')"

        If conexiones.executarsql(query) Then
            MsgBox("Asignación guardada", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESHABILITARTXT()
        Else
            MsgBox("Error al guardar asignación", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnModificar_Click(sender As Object, e As EventArgs) Handles btnModificar.Click
        If txtId.Text = "" Then
            MsgBox("Seleccione una asignación para modificar", MsgBoxStyle.Exclamation)
            Return
        End If

        If cmbBus.SelectedIndex = -1 Or cmbConductor.SelectedIndex = -1 Then
            MsgBox("Seleccione un bus y un conductor", MsgBoxStyle.Exclamation)
            Return
        End If

        Dim query As String =
            "UPDATE bus_conductor SET fk_matricula_bus='" & cmbBus.SelectedValue & "', " &
            "fk_cedula_conductor='" & cmbConductor.SelectedValue & "' " &
            "WHERE id_bus_conductor=" & txtId.Text

        If conexiones.executarsql(query) Then
            MsgBox("Asignación modificada", MsgBoxStyle.Information)
            cargar_grilla()
            LIMPIARTXT()
            DESHABILITARTXT()
        Else
            MsgBox("Error al modificar asignación", MsgBoxStyle.Critical)
        End If
    End Sub

    Private Sub btnEliminar_Click(sender As Object, e As EventArgs) Handles btnEliminar.Click
        If txtId.Text = "" Then
            MsgBox("Seleccione un registro para eliminar", MsgBoxStyle.Exclamation)
            Return
        End If

        If MsgBox("¿Está seguro de eliminar la asignación?", MsgBoxStyle.YesNo Or MsgBoxStyle.Question) = MsgBoxResult.Yes Then
            Dim query As String = "DELETE FROM bus_conductor WHERE id_bus_conductor=" & txtId.Text
            If conexiones.executarsql(query) Then
                MsgBox("Asignación eliminada", MsgBoxStyle.Information)
                cargar_grilla()
                LIMPIARTXT()
                DESHABILITARTXT()
            Else
                MsgBox("Error al eliminar asignación", MsgBoxStyle.Critical)
            End If
        End If
    End Sub

    Private Sub btnCerrar_Click(sender As Object, e As EventArgs) Handles btnCerrar.Click
        Me.Close()
    End Sub


    Private Sub dgvBusConductor_CellClick(sender As Object, e As DataGridViewCellEventArgs) Handles dgvBusConductor.CellClick
        Try
            If e.RowIndex >= 0 Then
                Dim fila = dgvBusConductor.Rows(e.RowIndex)

                txtId.Text = fila.Cells("id_bus_conductor").Value.ToString()
                cmbBus.SelectedValue = fila.Cells("matricula").Value.ToString()
                cmbConductor.SelectedValue = fila.Cells("cedula_conductor").Value.ToString()

                HABILITARTXT()
            End If
        Catch ex As Exception
            MsgBox("Error al seleccionar asignación: " & ex.Message, MsgBoxStyle.Critical)
        End Try
    End Sub

    Private Sub cargarBuses()
        Dim dt As DataTable = conexiones.consulta("SELECT matricula FROM bus")
        cmbBus.DataSource = dt
        cmbBus.DisplayMember = "matricula"
        cmbBus.ValueMember = "matricula"
        cmbBus.SelectedIndex = -1
    End Sub

    Private Sub cargarConductores()
        Dim dt As DataTable = conexiones.consulta("SELECT cedula, nombre || ' ' || apellido AS nombre FROM conductor")
        cmbConductor.DataSource = dt
        cmbConductor.DisplayMember = "nombre"
        cmbConductor.ValueMember = "cedula"
        cmbConductor.SelectedIndex = -1
    End Sub

    Sub HABILITARTXT()
        cmbBus.Enabled = True
        cmbConductor.Enabled = True
    End Sub

    Sub DESHABILITARTXT()
        cmbBus.Enabled = False
        cmbConductor.Enabled = False
    End Sub

    Sub LIMPIARTXT()
        txtId.Text = ""
        cmbBus.SelectedIndex = -1
        cmbConductor.SelectedIndex = -1
    End Sub

End Class