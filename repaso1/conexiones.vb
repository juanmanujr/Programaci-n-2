Imports Npgsql
Module Conexion
    Public CadenaConexion As String = "User ID=postgres;Password=Queteimporta9;Host=LocalHost;" &
                          "Port=5432;Database=repaso"

    'se crea una funcion para la consulta a la base de datos
    Public cod_usuario As Integer
    Public perfil As String

    Public Function consulta(ByVal coman As String) As DataTable
        Dim cnn As NpgsqlConnection = New NpgsqlConnection(CadenaConexion)
        cnn.Open()
        Dim dt As New DataTable
        Dim ds As New DataSet
        Dim da As NpgsqlDataAdapter = New NpgsqlDataAdapter(coman, cnn)
        da.Fill(dt)
        cnn.Close()
        Return (dt)
    End Function

    'funcion para ejecutar el insert, update, delete a la base de datos.
    Function ejecutarsql(ByVal coman As String) As Boolean
        Try
            Dim cnn As NpgsqlConnection = New NpgsqlConnection(CadenaConexion)
            cnn.Open()
            Dim ejecute As NpgsqlCommand = New NpgsqlCommand(coman, cnn)
            If ejecute.ExecuteNonQuery = 0 Then
                cnn.Close()
                Return False
            Else
                cnn.Close()
                Return True
            End If
        Catch ex As Exception
            MsgBox(ex.Message)
            Return False
        End Try
    End Function
End Module
